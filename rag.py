import streamlit as st
import openai
import time
import chromadb
from chromadb.utils import embedding_functions

# --------------------------
# Azure OpenAI Configuration
# --------------------------
openai.api_type = "azure"
openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
openai.api_version = "2025-01-01-preview"
openai.api_key = "FOObvelUv1Ubbw0ZlEb3NPCBYDbdXWbLhzyckQAA9cP3Ofhgi8KWJQQJ99BIACHYHv6XJ3w3AAAAACOGoHUz"

DEPLOYMENT_NAME = "gpt-35-turbo"
EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Initialize ChromaDB
# --------------------------
chroma_client = chromadb.PersistentClient(path="rag_db")

embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key,
    api_base=openai.api_base,
    api_type=openai.api_type,
    api_version=openai.api_version,
    model_name=EMBEDDING_DEPLOYMENT,
    deployment=EMBEDDING_DEPLOYMENT,
)

collection = chroma_client.get_or_create_collection(
    name="docs_collection", embedding_function=embedding_fn
)

# --------------------------
# Load documents into Chroma (one-time)
# --------------------------
if "docs_loaded" not in st.session_state:
    sample_docs = [
        {"id": "1", "content": "TESDA provides free technical vocational education and training."},
        {"id": "2", "content": "You can enroll in TESDA courses online via the TESDA Online Program."},
        {"id": "3", "content": "TESDA issues National Certificates to graduates who pass competency assessments."},
    ]
    for doc in sample_docs:
        collection.add(documents=[doc["content"]], ids=[doc["id"]])
    st.session_state.docs_loaded = True

# --------------------------
# Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful RAG chatbot. Use retrieved documents when possible."}
    ]

# --------------------------
# Display Chat
# --------------------------
st.title("🤖 RAG Chatbot with Azure OpenAI + ChromaDB")

for msg in st.session_state.messages:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
    st.markdown(f"**{role}:** {msg['content']}")

# --------------------------
# User Input
# --------------------------
user_input = st.text_input("Ask a question:")

if st.button("🚀 Send") and user_input.strip():
    # Retrieve relevant docs
    results = collection.query(query_texts=[user_input], n_results=2)
    retrieved_texts = " ".join(results["documents"][0]) if results["documents"] else ""

    # Build augmented prompt
    augmented_query = f"User question: {user_input}\n\nRelevant info:\n{retrieved_texts}\n\nAnswer clearly:"

    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("🤖 Thinking..."):
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,
                messages=st.session_state.messages + [{"role": "system", "content": augmented_query}],
                temperature=0.5,
                max_tokens=500
            )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# --------------------------
# Reset Button
# --------------------------
if st.button("🔄 Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful RAG chatbot. Use retrieved documents when possible."}
    ]
    st.rerun()
