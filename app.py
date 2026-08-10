import streamlit as st
from pathlib import Path
from rag_backend import query_rag, CHROMA_DIR

st.set_page_config(
    page_title="Assistente Mercado Central 24h",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 Assistente Virtual - Mercado Central 24h")
st.markdown("Tire suas dúvidas sobre o Regulamento Interno, Políticas de Troca, FAQ e Manual de Fornecedores.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    profile = st.selectbox(
        "Perfil do Usuário",
        ["Cliente", "Funcionário", "Fornecedor"]
    )
    
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("**Sobre o Sistema**")
    st.markdown("Assistente RAG alimentado por IA (Groq & LangChain) baseado nos manuais oficiais do Mercado Central 24h.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "fontes" in message and message["fontes"]:
            with st.expander("📚 Ver fontes consultadas"):
                for fonte in message["fontes"]:
                    st.markdown(f"- `{fonte}`")

# React to user input
if user_input := st.chat_input("Digite sua dúvida aqui..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Consultando manuais do Mercado Central..."):
            try:
                result = query_rag(
                    user_query=user_input,
                    chat_history=st.session_state.messages[:-1],
                    profile=profile
                )
                response_text = result["resposta"]
                sources = result["fontes"]
                
                st.markdown(response_text)
                
                if sources:
                    with st.expander("📚 Ver fontes consultadas"):
                        for fonte in sources:
                            st.markdown(f"- `{fonte}`")
                            
                # Save assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "fontes": sources
                })
            except Exception as e:
                error_msg = f"Erro ao processar consulta: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "fontes": []
                })
