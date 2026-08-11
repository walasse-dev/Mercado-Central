# 🛒 Assistente Virtual RAG — Mercado Central 24h

Sistema inteligente de atendimento, suporte e consulta baseado em **RAG (Retrieval-Augmented Generation)** utilizando LangChain, ChromaDB, HuggingFace Embeddings (`all-MiniLM-L6-v2`), Google Gemini (`gemini-3.5-flash-lite`) e Streamlit.

---

## 📋 1. Visão Geral do Sistema

O **Assistente Virtual do Mercado Central 24h** foi desenvolvido para solucionar dúvidas operacionais de colaboradores, clientes e fornecedores de forma rápida, precisa e estritamente fundamentada nos documentos institucionais oficiais da empresa.

### 📚 Documentos Institucionais Base:
1. `Regulamento Interno e Procedimentos Operacionais — Mercado Central 24h`
2. `Política de Atendimento, Trocas e Devoluções — Mercado Central 24h`
3. `Perguntas Frequentes (FAQ) — Clientes e Funcionários — Mercado Central 24h`
4. `Manual de Fornecedores e Política de Compras — Mercado Central 24h`

---

## 🏗️ 2. Arquitetura da Solução

```
[Documentos PDF Institucionais]
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND RAG                           │
│  1. Ingestão e Leitura (PyPDFLoader)                        │
│  2. Fragmentação de Texto (RecursiveCharacterTextSplitter)  │
│  3. Vetorização (all-MiniLM-L6-v2 via HuggingFace)          │
│  4. Armazenamento Vetorial Local (ChromaDB)                 │
│  5. Recuperação Híbrida & Filtragem por Metadados (Audience)│
└──────────────────────────────┬──────────────────────────────┘
                               │ (Chamada RAG com Gemini 3.5 Flash Lite)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND STREAMLIT                      │
│  1. Interface de Chat Interativa (st.chat_message)          │
│  2. Seleção de Perfil (Cliente, Funcionário, Fornecedor)    │
│  3. Histórico de Sessão e Limpeza de Conversa               │
│  4. Expansão de Fontes e Trechos Consultados nos Manuais    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 3. Requisitos de Ambiente e Dependências

### 3.1 Requisitos de Software
* **Python:** Versão 3.10 ou superior
* **Gerenciador de Pacotes:** `pip`

### 3.2 Pacotes Principais (`requirements.txt`)
* `streamlit`
* `langchain`
* `langchain-community`
* `langchain-huggingface`
* `langchain-google-genai`
* `sentence-transformers`
* `chromadb`
* `pypdf`
* `python-dotenv`

---

## ⚙️ 4. Configuração e Instalação Local

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/Mercado-Central.git
cd Mercado-Central
```

### Passo 2: Criar e Ativar o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### Passo 3: Instalar as Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com a sua chave de API do Google Gemini (`GEMINI_API_KEY` ou `GOOGLE_API_KEY`):
```env
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### Passo 5: Executar a Aplicação Localmente
```bash
streamlit run app.py
```
Acesse o aplicativo no navegador em `http://localhost:8501`.

---

## 🚀 5. Deploy no Streamlit Community Cloud

Para colocar o aplicativo no ar acessível publicamente 24/7:

1. Suba o código para um repositório no GitHub (mantenha a pasta `docs/` e `chroma_db/`).
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e faça login com sua conta do GitHub.
3. Clique em **"New app"** e selecione seu repositório, branch (`main`) e arquivo principal (`app.py`).
4. Em **Advanced settings -> Secrets**, adicione sua chave de API:
   ```toml
   GEMINI_API_KEY = "sua_chave_gemini_aqui"
   ```
5. Clique em **Deploy!**

---

## 🔒 6. Política de Segurança e Controle de Acesso por Perfil

O assistente possui restrições rígidas em seu backend e prompt de sistema para garantir conformidade e segurança:
* **Filtros de Perfil em Camada Dupla:** O recuperador aplica filtros de metadados (`audience`: *Geral*, *Funcionário*, *Fornecedor*) garantindo que Clientes não acessem normas internas de Funcionários ou Manuais de Fornecedores.
* **Mensagens Padronizadas:** Tentativas de acesso não autorizado retornam mensagens específicas, como *"Você precisa ser um funcionário para receber essa informação."*
* **Domínio Estrito:** Responde apenas com base nos documentos institucionais do Mercado Central 24h, rejeitando perguntas de conhecimento geral.
* **Citação de Fontes:** Sempre exibe expansores detalhando quais manuais e trechos foram consultados para formular a resposta.

---

## 🧪 7. Perguntas Recomendadas para Testes

### Como Cliente:
* *"Qual é o prazo e as condições para troca de produtos perecíveis?"*
* *"Como funciona a política de reembolso em caso de desistência?"*
* *(Tentativa de Acesso Restrito)* *"Quais são os procedimentos de segurança e abertura de caixa?"* $\rightarrow$ *Deve retornar a mensagem de restrição.*

### Como Funcionário:
* *"Quais são os procedimentos de segurança e abertura de caixa?"*
* *"Qual o protocolo em caso de divergência de estoque?"*

### Como Fornecedor:
* *"Quais são os prazos de pagamento estipulados para compras?"*
* *"Quais os requisitos de recebimento e conferência cega?"*

---

## 📁 8. Estrutura de Pastas do Projeto

```text
Mercado-Central/
├── app.py                      # Interface Web Streamlit
├── rag_backend.py              # Lógica RAG (LangChain, ChromaDB, Gemini)
├── requirements.txt            # Dependências do Python
├── .env                        # Variáveis de ambiente (local)
├── .gitignore                  # Arquivos ignorados pelo Git
├── docs/                       # Manuais institucionais em PDF
│   ├── Regulamento Interno...pdf
│   ├── Política de Atendimento...pdf
│   ├── Perguntas Frequentes (FAQ)...pdf
│   └── Manual de Fornecedores...pdf
└── chroma_db/                  # Banco vetorial local indexado
```

---
*Desenvolvido para o Mercado Central 24h — Powered by Google Gemini 3.5 Flash Lite.*
