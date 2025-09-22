# app.py
import streamlit as st
import openai
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# --------------------------
# Azure OpenAI Configuration
# --------------------------
openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = "MyKey"

# --------------------------
# Load Embedding Model
# --------------------------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------
# Build / Load FAISS Index
# --------------------------
@st.cache_resource
def load_vectorstore():
    try:
        with open("vectorstore.pkl", "rb") as f:
            return pickle.load(f)
    except:
        index = faiss.IndexFlatL2(384)  # 384 dims for MiniLM
        return {"index": index, "docs": []}

vectorstore = load_vectorstore()

def add_document(text: str):
    embedding = embed_model.encode([text])
    vectorstore["index"].add(embedding)
    vectorstore["docs"].append(text)
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

def retrieve(query: str, k=3):
    embedding = embed_model.encode([query])
    D, I = vectorstore["index"].search(embedding, k)
    return [vectorstore["docs"][i] for i in I[0] if i < len(vectorstore["docs"])]

# --------------------------
# Chatbot Response
# --------------------------
def chatbot_response(user_message: str) -> str:
    # Step 1: Retrieve
    retrieved_docs = retrieve(user_message, k=3)
    context = "\n".join(retrieved_docs) if retrieved_docs else "No context found."

    # Step 2: Augment prompt
    prompt = f"""
    You are a helpful assistant. Use the following context to answer:
    Context: {context}
    Question: {user_message}
    Answer:
    """

    # Step 3: Call Azure OpenAI
    response = openai.ChatCompletion.create(
        engine="gpt-4o-mini",   # Replace with your deployed model name
        messages=[
            {"role": "system", "content": "You are a RAG chatbot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400
    )

    return response["choices"][0]["message"]["content"]

# --------------------------
# Streamlit UI
# --------------------------
st.title("🔎 RAG Chatbot (Azure OpenAI + Streamlit)")

with st.sidebar:
    st.header("📄 Add Documents")
    doc_text = st.text_area("Paste a document:")
    if st.button("Add to Knowledge Base"):
        if doc_text.strip():
            add_document(doc_text.strip())
            st.success("Document added!")

user_input = st.text_input("Ask me anything:")
if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            answer = chatbot_response(user_input)
        st.markdown(f"**Answer:** {answer}")
