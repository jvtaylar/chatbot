# --- sqlite compatibility shim ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass
# --------------------------------


import streamlit as st
import openai
import time
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores import Chroma

# --------------------------
# Azure OpenAI Configuration
# --------------------------
openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = "FOObvelUv1Ubbw0ZlEb3NPCBYDbdXWbLhzyckQAA9cP3Ofhgi8KWJQQJ99BIACHYHv6XJ3w3AAAAACOGoHUz"
DEPLOYMENT_NAME = "gpt-35-turbo"

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="RAG Copilot Chatbot", page_icon="📘", layout="wide")

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This AI chatbot is powered by **Azure OpenAI + RAG (ChromaDB)**")
    st.markdown("""
    ✅ Upload PDFs  
    ✅ Ask questions from documents  
    ✅ Context-aware answers  
    """)

# --------------------------
# Upload PDF & Build Knowledge Base
# --------------------------
uploaded_file = st.file_uploader("📂 Upload a PDF knowledge base", type=["pdf"])

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # Create embeddings & vectorstore
    embeddings = AzureOpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key=openai.api_key,
        azure_endpoint=openai.api_base
    )

    vectordb = Chroma.from_texts(chunks, embeddings, persist_directory="rag_db")
    retriever = vectordb.as_retriever()

else:
    retriever = None

# --------------------------
# Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant that uses both general knowledge and the uploaded document context."}
    ]

# --------------------------
# Display Messages
# --------------------------
st.markdown("<h1 style='text-align: center; color: #0078D7;'>📘 RAG Copilot Chatbot</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='background:#DCF8C6; padding:10px; border-radius:10px; margin:5px; text-align:right;'>🧑 <b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div style='background:#E6E6FA; padding:10px; border-radius:10px; margin:5px; text-align:left;'>🤖 <b>Bot:</b> {msg['content']}</div>", unsafe_allow_html=True)

# --------------------------
# User Input
# --------------------------
st.markdown("### ✍️ Ask your question")
user_input = st.text_input("Type your question here:")

if st.button("🚀 Send") and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("🤖 Bot is searching..."):
            context = ""
            if retriever:
                docs = retriever.get_relevant_documents(user_input)
                context = "\n".join([d.page_content for d in docs])

            # Combine user query with retrieved context
            system_prompt = f"Use the following context to answer:\n{context}\n\nQuestion: {user_input}"

            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a RAG-based assistant. Always cite from context if relevant."},
                    {"role": "user", "content": system_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# --------------------------
# Reset Chat
# --------------------------
if st.button("🔄 Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant with RAG context."}
    ]
    st.rerun()
