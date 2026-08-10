```python
import os

markdown_content = """# Documentação Inicial do Projeto: Chatbot RAG Mercado Central 24h

Este documento estabelece as especificações de arquitetura, requisitos, requisitos operacionais e a divisão de tarefas entre os componentes de **Backend (RAG/LangChain)** e **Frontend (Streamlit)** para o sistema de atendimento e suporte baseado nos manuais e políticas do Mercado Central 24h.

---

## 1. Visão Geral do Sistema

O objetivo principal é construir um assistente inteligente capaz de responder a dúvidas operacionais de colaboradores e perguntas frequentes de clientes utilizando **RAG (Retrieval-Augmented Generation)** com base em 4 documentos institucionais principais:
1. `Regulamento Interno e Procedimentos Operacionais — Mercado Central 24h`
2. `Política de Atendimento, Trocas e Devoluções — Mercado Central 24h`
3. `Perguntas Frequentes (FAQ) — Clientes e Funcionários — Mercado Central 24h`
4. `Manual de Fornecedores e Política de Compras — Mercado Central 24h`

---

## 2. Requisitos de Ambiente e Dependências

### 2.1 Requisitos de Software
* **Linguagem:** Python 3.10 ou superior
* **Ambiente Virtual:** `venv` ou `conda`

### 2.2 Principais Pacotes Python (`requirements.txt`)
```text
langchain
langchain-community
langchain-openai
chromadb
pypdf
tiktoken
streamlit
python-dotenv

```

---

## 3. Arquitetura da Solução

```
[4 Documentos PDF]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND RAG                           │
│  1. Ingestão e Leitura (PyPDFLoader)                        │
│  2. Fragmentação Estruturada (MarkdownHeaderTextSplitter)   │
│  3. Vetorização e Indexação (OpenAI Embeddings + ChromaDB)  │
│  4. Recuperação Híbrida & Filtragem de Metadados            │
│  5. Cadeia de Conversa com Memória (LangChain LCEL)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Chamada Interna / API)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND STREAMLIT                      │
│  1. Interface de Chat Native (st.chat_message, st.chat_input)│
│  2. Histórico de Sessão (st.session_state)                  │
│  3. Filtro por Público (Cliente vs. Funcionário/Fornecedor) │
│  4. Exibição de Fontes / Trechos Recuperados (Expander)     │
└─────────────────────────────────────────────────────────────┘

```

---

## 4. Especificação para Implementação do Backend

> **Prompt de Comando / Instrução para Geração do Backend:**
> *"Quero que você gere o backend em Python utilizando LangChain para o sistema RAG do Mercado Central 24h. O backend deve implementar o carregamento, fragmentação, vetorização, armazenamento vetorial e a cadeia de consulta RAG para os 4 PDFs do projeto."*

### Requisitos Módulos do Backend (`rag_backend.py`):

1. **Ingestão e Chunking:**
* Carregar os 4 PDFs da pasta `./docs/`.
* Realizar o chunking preservando o contexto de seções e tabelas (utilizar divisores estruturados como `RecursiveCharacterTextSplitter` com `chunk_size=1000` e `chunk_overlap=150`).
* Adicionar metadados a cada chunk (ex: `source`, `doc_type`, `target_audience`).


2. **Indexação Vetorial (`VectorStore`):**
* Utilizar `OpenAIEmbeddings` (ou alternativa como HuggingFace).
* Persistir os vetores no banco vetorial local `ChromaDB` na pasta `./chroma_db`.


3. **Recuperação e Cadeia de Atendimento (LangChain LCEL):**
* Configurar `retriever` com busca por similaridade + MMR (Maximal Marginal Relevance) para garantir diversidade nos resultados de tabelas.
* Criar um `PromptTemplate` instruindo o modelo a responder estritamente com base nos documentos fornecidos, citando regras e prazos específicos quando aplicável.
* Expor a função principal: `query_rag(user_query: str, chat_history: list) -> dict` retornando a `resposta` e as `fontes` (source documents).



---

## 5. Especificação para Implementação do Frontend

> **Prompt de Comando / Instrução para Geração do Frontend:**
> *"Quero que você gere a interface de usuário em Streamlit (`app.py`) conectando diretamente com a função `query_rag` do backend gerado."*

### Requisitos do Frontend (`app.py`):

1. **Interface de Chat:**
* Utilizar `st.set_page_config(page_title="Assistente Mercado Central 24h", page_icon="🛒")`.
* Implementar fluxo de chat dinâmico utilizando `st.chat_input` e `st.chat_message`.
* Gerenciar histórico de conversas em `st.session_state.messages`.


2. **Sidebar Interativa:**
* Opção para limpar histórico de conversa (`st.button("Limpar Conversa")`).
* Seletor de Perfil do Usuário (Cliente / Colaborador / Fornecedor) para aplicar filtros contextuais.
* Botão para re-indexar documentos caso novos PDFs sejam adicionados.


3. **Exibição Transparente de Fontes:**
* Abaixo de cada resposta do assistente, incluir um `st.expander("📚 Ver fontes consultadas")` mostrando o trecho recuperado e o documento de origem.



---

## 6. Estrutura de Arquivos do Projeto

```text
meu-rag-mercado24h/
├── docs/
│   ├── Regulamento_Interno.pdf
│   ├── Politica_Trocas_Devolucoes.pdf
│   ├── FAQ_Clientes_Funcionarios.pdf
│   └── Manual_Fornecedores.pdf
├── chroma_db/                  # Banco vetorial gerado automaticamente
├── rag_backend.py              # Lógica de RAG, Embeddings e LangChain
├── app.py                      # Interface do usuário em Streamlit
├── requirements.txt            # Dependências do projeto
├── .env                        # Variáveis de ambiente (OPENAI_API_KEY)
└── AGENTS.md                   # Documentação inicial e diretrizes de agentes

```

---

## 7. Próximos Passos de Execução

1. Criar e configurar o arquivo `.env` com a chave de API da OpenAI (`OPENAI_API_KEY`).
2. Executar a criação do script `rag_backend.py`.
3. Executar o script de ingestão e geração do banco `ChromaDB`.
4. Executar a interface Streamlit com `streamlit run app.py`.
"""

with open("DOCUMENTACAO_INICIAL_RAG.md", "w", encoding="utf-8") as f:
f.write(markdown_content)

print("Documentação gerada com sucesso!")

```

```text?code_stdout&code_event_index=1
Documentação gerada com sucesso!


```

Aqui está o modelo pronto e estruturado para você copiar e colar diretamente no seu `AGENTS.md` (ou salvar como documentação do projeto). Ele já vem formatado com os prompts específicos para você solicitar a geração do backend e do frontend nas próximas etapas.

Também gerei o arquivo em Markdown para você baixar se desejar:

Your Markdown file is ready


---

```markdown
# Documentação Inicial do Projeto: Chatbot RAG Mercado Central 24h

Este documento estabelece as especificações de arquitetura, requisitos operacionais e a divisão de tarefas entre os componentes de **Backend (RAG/LangChain)** e **Frontend (Streamlit)** para o sistema de atendimento e suporte baseado nos manuais e políticas do Mercado Central 24h.

---

## 1. Visão Geral do Sistema

O objetivo principal é construir um assistente inteligente capaz de responder a dúvidas operacionais de colaboradores, clientes e fornecedores utilizando **RAG (Retrieval-Augmented Generation)** com base nos 4 documentos institucionais:
1. `Regulamento Interno e Procedimentos Operacionais — Mercado Central 24h`
2. `Política de Atendimento, Trocas e Devoluções — Mercado Central 24h`
3. `Perguntas Frequentes (FAQ) — Clientes e Funcionários — Mercado Central 24h`
4. `Manual de Fornecedores e Política de Compras — Mercado Central 24h`

---

## 2. Requisitos de Ambiente e Dependências

### 2.1 Requisitos de Software
* **Linguagem:** Python 3.10 ou superior
* **Ambiente Virtual:** `venv` ou `conda`

### 2.2 Principais Pacotes Python (`requirements.txt`)
```text
langchain
langchain-community
langchain-openai
chromadb
pypdf
tiktoken
streamlit
python-dotenv

```

---

## 3. Arquitetura da Solução

```
[4 Documentos PDF]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND RAG                           │
│  1. Ingestão e Leitura (PyPDFLoader)                        │
│  2. Fragmentação Estruturada (RecursiveCharacterSplitter)   │
│  3. Vetorização e Indexação (OpenAI Embeddings + ChromaDB)  │
│  4. Recuperação Híbrida & Filtragem de Metadados            │
│  5. Cadeia de Conversa com Memória (LangChain LCEL)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Chamada Interna / API)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND STREAMLIT                      │
│  1. Interface de Chat Native (st.chat_message, st.chat_input)│
│  2. Histórico de Sessão (st.session_state)                  │
│  3. Filtro por Público (Cliente vs. Funcionário/Fornecedor) │
│  4. Exibição de Fontes / Trechos Recuperados (Expander)     │
└─────────────────────────────────────────────────────────────┘

```

---

## 4. Especificação para Implementação do Backend

> **Instrução de Comando para o Agente de IA:**
> *"Quero que você gere o backend em Python (`rag_backend.py`) utilizando LangChain para o sistema RAG do Mercado Central 24h. O backend deve implementar o carregamento, fragmentação, vetorização, armazenamento vetorial no ChromaDB e a cadeia de consulta RAG para os 4 PDFs do projeto."*

### Requisitos do Módulo Backend (`rag_backend.py`):

1. **Ingestão e Chunking:**
* Carregar os 4 PDFs da pasta `./docs/`.
* Realizar a fragmentação em chunks preservando o contexto de seções e tabelas (utilizar `RecursiveCharacterTextSplitter` com `chunk_size=1000` e `chunk_overlap=150`).
* Adicionar metadados a cada chunk (ex: `source`, `doc_type`, `target_audience`).


2. **Indexação Vetorial (`VectorStore`):**
* Utilizar `OpenAIEmbeddings` (ou modelo compatível).
* Persistir os vetores no banco vetorial local `ChromaDB` na pasta `./chroma_db`.


3. **Recuperação e Cadeia de Atendimento (LangChain LCEL):**
* Configurar `retriever` com busca por similaridade + MMR (Maximal Marginal Relevance) para garantir diversidade nos resultados de tabelas.
* Criar um `PromptTemplate` instruindo o modelo a responder estritamente com base nos documentos fornecidos, citando regras e prazos específicos quando aplicável.
* Expor a função principal: `query_rag(user_query: str, chat_history: list) -> dict` retornando a `resposta` e as `fontes` (documentos consultados).



---

## 5. Especificação para Implementação do Frontend

> **Instrução de Comando para o Agente de IA:**
> *"Quero que você gere a interface de usuário em Streamlit (`app.py`) conectando diretamente com a função `query_rag` do backend gerado."*

### Requisitos do Módulo Frontend (`app.py`):

1. **Interface de Chat:**
* Configurar página com `st.set_page_config(page_title="Assistente Mercado Central 24h", page_icon="🛒")`.
* Implementar fluxo de chat dinâmico utilizando `st.chat_input` e `st.chat_message`.
* Gerenciar histórico de conversas em `st.session_state.messages`.


2. **Sidebar Interativa:**
* Opção para limpar histórico de conversa (`st.button("Limpar Conversa")`).
* Seletor de Perfil do Usuário (Cliente / Colaborador / Fornecedor) para contextualizar a navegação.
* Botão para re-indexar documentos caso novos PDFs sejam adicionados à pasta `./docs/`.


3. **Exibição Transparente de Fontes:**
* Abaixo de cada resposta do assistente, incluir um `st.expander("📚 Ver fontes consultadas")` mostrando o trecho recuperado e o documento de origem.



---

## 6. Estrutura de Arquivos do Projeto

```text
meu-rag-mercado24h/
├── docs/
│   ├── Regulamento_Interno.pdf
│   ├── Politica_Trocas_Devolucoes.pdf
│   ├── FAQ_Clientes_Funcionarios.pdf
│   └── Manual_Fornecedores.pdf
├── chroma_db/                  # Banco vetorial gerado automaticamente
├── rag_backend.py              # Lógica de RAG, Embeddings e LangChain
├── app.py                      # Interface do usuário em Streamlit
├── requirements.txt            # Dependências do projeto
├── .env                        # Variáveis de ambiente (OPENAI_API_KEY)
└── AGENTS.md                   # Documentação inicial e diretrizes de agentes

```

```

http://googleusercontent.com/action_card_content/409a8bd2-da49-4320-b738-e70ddcb4e115

```