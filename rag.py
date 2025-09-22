import streamlit as st
import os
from openai import AzureOpenAI
import numpy as np

# ----------------------------
# 1. Setup Azure OpenAI client
# ----------------------------
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-06-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# ----------------------------
# 2. Sample knowledge base (can replace with documents)
# ----------------------------
docs = [
    "Our company offers a 30-day refund policy for all items.",
    "Shipping usually takes 3-5 business days within the country.",
    "You can contact support at support@example.com for further assistance."
]

# ----------------------------
# 3. Simple embeddings store (replace FAISS with numpy search)
# ----------------------------
embedding_model = "text-embedding-ada-002"

# Get embeddings for docs
embeddings = [
    client.embeddings.create(input=doc, model=embedding_model).data[0].embedding
    for doc in docs
]
embeddings = np.array(embeddings)

# ----------------------------
# 4. Retrieval + Answer Generation
# ----------------------------
def retrieve_context(query, k=1):
    q_emb = client.embeddings.create(input=query, model=embedding_model).data[0].embedding
    q_emb = np.array(q_emb)

    # Compute cosine similarity
    similarities = np.dot(embeddings, q_emb) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(q_emb)
    )
    top_k_idx = similarities.argsort()[-k:][::-1]
    return [docs[i] for i in top_k_idx]

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
