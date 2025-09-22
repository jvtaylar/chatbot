import streamlit as st
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from PyPDF2 import PdfReader
import os

# --------------------------
# Azure OpenAI Configuration
# --------------------------
AZURE_OPENAI_API_KEY = "your_azure_api_key"
AZURE_OPENAI_ENDPOINT = "https://your-resource-name.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-35-turbo"   # your deployment name
EMBEDDING_MODEL = "text-embedding-ada-002"

# --------------------------
# Initialize LLM and Embeddings
# --------------------------
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    deployment_name=DEPLOYMENT_NAME,
    api_version="2024-02-15-preview"
)

embeddings = AzureOpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# --------------------------
# Streamlit UI
# --------------------------
st.title("📘 TESDA RAG Chatbot with PDF Upload")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Extract text from PDF
    pdf_reader = PdfReader(uploaded_file)
    raw_text = ""
    for page in pdf_reader.pages:
        raw_text += page.extract_text() + "\n"

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents([Document(page_content=raw_text)])

    # Build vector DB
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory="chroma_db")
    retriever = vectordb.as_retriever()

    # Retrieval QA Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    # User Input
    user_question = st.text_input("Ask me anything from the uploaded PDF:")

    if user_question:
        answer = qa_chain.run(user_question)
        st.write("**Answer:**", answer)
