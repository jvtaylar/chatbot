import streamlit as st
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.chains import RetrievalQA
# from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS


# --------------------------
# Azure OpenAI Configuration
# --------------------------
AZURE_OPENAI_API_KEY = "FOObvelUv1Ubbw0ZlEb3NPCBYDbdXWbLhzyckQAA9cP3Ofhgi8KWJQQJ99BIACHYHv6XJ3w3AAAAACOGoHUz"
AZURE_OPENAI_ENDPOINT = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
DEPLOYMENT_NAME = "gpt-35-turbo"   # your deployment name
EMBEDDING_MODEL = "text-embedding-ada-002"

# --------------------------
# Initialize LLM and Embeddings
# --------------------------
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    deployment_name=DEPLOYMENT_NAME,
    api_version="2025-01-01-preview"
)

embeddings = AzureOpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# --------------------------
# Sample Knowledge Base (replace with your documents/FAQs)
# --------------------------
texts = [
    "TESDA offers various technical vocational education and training programs in the Philippines.",
    "To enroll in TESDA, you need to register through the TESDA app or their website.",
    "TESDA provides assessment and certification for skilled workers."
]
docs = [Document(page_content=t) for t in texts]

# Split docs (if they are long)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

# --------------------------
# Create Vector Database
# --------------------------
# vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory="chroma_db")
# retriever = vectordb.as_retriever()
vectordb = FAISS.from_documents(split_docs, embeddings)
retriever = vectordb.as_retriever()

# --------------------------
# Retrieval-Augmented QA Chain
# --------------------------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff"
)

# --------------------------
# Streamlit UI
# --------------------------
st.title("TESDA RAG Chatbot 🤖")

user_question = st.text_input("Ask me anything about TESDA:")

if user_question:
    answer = qa_chain.run(user_question)
    st.write("**Answer:**", answer)
