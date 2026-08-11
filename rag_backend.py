import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

DOCS_DIR = Path("./docs")
CHROMA_DIR = Path("./chroma_db")

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def initialize_vectorstore():
    embeddings = get_embeddings()
    
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        return Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    
    docs = []
    if DOCS_DIR.exists():
        for pdf_path in DOCS_DIR.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            
            filename = pdf_path.name
            if "Regulamento Interno" in filename:
                audience = "Funcionário"
            elif "Manual de Fornecedores" in filename:
                audience = "Fornecedor"
            else:
                audience = "Geral"
                
            for page in pages:
                page.metadata["source"] = filename
                page.metadata["audience"] = audience
                docs.append(page)
                
    if not docs:
        raise ValueError("Nenhum documento PDF encontrado na pasta ./docs/")
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = text_splitter.split_documents(docs)
    
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    return vectorstore

def query_rag(user_query: str, chat_history: list = None, profile: str = "Cliente") -> dict:
    if chat_history is None:
        chat_history = []
        
    vectorstore = initialize_vectorstore()
    
    # Validação direcionada para Clientes tentando acessar procedimentos estritamente internos
    if profile == "Cliente":
        query_lower = user_query.lower()
        internal_keywords = ["caixa", "sangria", "abertura de caixa", "segurança do caixa", "uniforme", "celular", "ponto eletrônico", "escala de trabalho"]
        if any(kw in query_lower for kw in internal_keywords):
            unfiltered_docs = vectorstore.similarity_search(user_query, k=1)
            if unfiltered_docs and "Regulamento Interno" in unfiltered_docs[0].metadata.get("source", ""):
                return {
                    "resposta": "Você precisa ser um funcionário para receber essa informação.",
                    "fontes": [unfiltered_docs[0].metadata.get("source", "Desconhecido")],
                    "docs_detalhes": unfiltered_docs
                }

    # Configurar o filtro de metadados baseado no perfil
    search_filter = None
    if profile == "Cliente":
        search_filter = {"audience": "Geral"}
    elif profile == "Fornecedor":
        search_filter = {"audience": {"$in": ["Geral", "Fornecedor"]}}

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            **({"filter": search_filter} if search_filter else {})
        }
    )
    
    relevant_docs = retriever.invoke(user_query)
    sources = set(doc.metadata.get("source", "Desconhecido") for doc in relevant_docs)

    # Format context with audience metadata indication
    formatted_chunks = []
    for doc in relevant_docs:
        source = doc.metadata.get("source", "Desconhecido")
        audience = doc.metadata.get("audience", "Geral")
        chunk_str = f"[Documento: {source} | Público-Alvo: {audience}]\n{doc.page_content}"
        formatted_chunks.append(chunk_str)
        
    context_text = "\n\n--- [Trecho de Documento] ---\n".join(formatted_chunks)
    
    system_prompt = f"""Você é o agente virtual oficial do Mercado Central 24h.
O usuário atual está acessando o sistema com o perfil: "{profile}" (opções válidas: Cliente, Funcionário, Fornecedor).
Sua função exclusiva é responder dúvidas com base estritamente nos documentos institucionais fornecidos abaixo.

Se a pergunta do usuário não estiver relacionada ao Mercado Central 24h ou não constar nos documentos fornecidos, recuse-se estritamente a responder utilizando conhecimento geral. Informe educadamente que você é um assistente dedicado exclusivamente ao suporte dos manuais do Mercado Central 24h.

Nunca utilize placeholders como [Nome do Atendente] nem solicite CPF ou número de cupom fiscal.
Cite regras, prazos e seções específicas sempre que aplicável.

Contexto Recuperado:
{context_text}
"""

    lc_messages = [SystemMessage(content=system_prompt)]
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=user_query))
    
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada no arquivo .env ou variáveis de ambiente.")
        
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0.3,
            google_api_key=gemini_api_key
        )
        response = llm.invoke(lc_messages)
        resposta = response.content
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            resposta = "O sistema atingiu temporariamente o limite de requisições da API do Google Gemini. Por favor, aguarde alguns instantes e tente novamente."
        else:
            raise e
    
    return {
        "resposta": resposta,
        "fontes": list(sources),
        "docs_detalhes": relevant_docs
    }
