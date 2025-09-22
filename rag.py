import streamlit as st
import os
from openai import AzureOpenAI
import faiss
import tiktoken
import numpy as np

# ----------------------------
# 1. Setup Azure OpenAI client
# ----------------------------
openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = "MyKey"

DEPLOYMENT_NAME = "gpt-35-turbo"
# ----------------------------
# 2. Sample knowledge base (can replace with documents)
# ----------------------------
docs = [
    "Our company offers a 30-day refund policy for all items.",
    "Shipping usually takes 3-5 business days within the country.",
    "You can contact support at support@example.com for further assistance."
]

# ----------------------------
# 3. Create embeddings + FAISS index
# ----------------------------
embedding_model = "text-embedding-ada-002"

# Get embeddings for docs
embeddings = [
    client.embeddings.create(input=doc, model=embedding_model).data[0].embedding
    for doc in docs
]

# Build FAISS index
dim = len(embeddings[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype('float32'))

# ----------------------------
# 4. Retrieval + Answer Generation
# ----------------------------
def retrieve_context(query, k=1):
    q_emb = client.embeddings.create(input=query, model=embedding_model).data[0].embedding
    q_emb = np.array([q_emb]).astype('float32')
    D, I = index.search(q_emb, k)
    return [docs[i] for i in I[0]]

def generate_answer(query):
    context = retrieve_context(query)
    prompt = f"Answer the question using the context below. If not relevant, say you don’t know.\n\nContext: {context}\n\nQuestion: {query}\nAnswer:"

    response = client.chat.completions.create(
        model="gpt-35-turbo",  # or gpt-4 if available
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# ----------------------------
# 5. Streamlit UI
# ----------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("🔎 RAG Chatbot with Azure OpenAI")

user_query = st.text_input("Ask a question:")

if user_query:
    answer = generate_answer(user_query)
    st.write("**Answer:**", answer)
