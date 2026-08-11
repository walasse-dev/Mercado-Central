import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

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
            for page in pages:
                page.metadata["source"] = pdf_path.name
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
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10}
    )
    
    relevant_docs = retriever.invoke(user_query)
    context_text = "\n\n--- [Trecho de Documento] ---\n".join([doc.page_content for doc in relevant_docs])
    
    sources = set(doc.metadata.get("source", "Desconhecido") for doc in relevant_docs)
    
    system_prompt = f"""Você é o agente virtual oficial do Mercado Central 24h.
Responda diretamente e profissionalmente à pergunta do usuário ({profile}) com base estritamente nos documentos institucionais fornecidos abaixo.
Nunca utilize placeholders genéricos como [Nome do Atendente] nem solicite CPF ou número de cupom fiscal, a menos que estritamente necessário pelo contexto da pergunta.
Se a informação não estiver nos documentos, informe educadamente que não encontrou essa diretriz nos manuais oficiais.
Cite regras, prazos e seções específicas sempre que aplicável.

Contexto Recuperado:
{context_text}
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add recent chat history if any (last 4 turns)
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_query})
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY não encontrada no arquivo .env ou variáveis de ambiente.")
        
    client = Groq(api_key=groq_api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_completion_tokens=2048,
        top_p=1,
        stream=False,
        stop=None
    )
    
    resposta = completion.choices[0].message.content
    
    return {
        "resposta": resposta,
        "fontes": list(sources),
        "docs_detalhes": relevant_docs
    }
