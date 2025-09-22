# app.py
import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List
import os
import textwrap

# --------------------------
# Azure OpenAI Configuration (use your values)
# --------------------------
import openai as _openai
_openai.api_type = "azure"
_openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
_openai.api_version = "2025-01-01-preview"
_openai.api_key = "MyKey"   # <<--- Replace with your real key

# Azure deployment/model name (replace with your actual deployed model)
AZURE_DEPLOYMENT_NAME = "gpt-4o-mini"  # replace with your actual deployment name

# A little wrapper so other parts of the code read from this module variable
openai = _openai

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="TESDA FAQ RAG Chatbot", layout="wide")
st.title("📚 TESDA Customer Support — RAG Chatbot (Streamlit + Azure OpenAI)")

cols = st.columns([3, 1])
left, right = cols

with right:
    st.header("Knowledge Base")
    st.markdown(
        "This app will scrape a set of TESDA FAQ pages, embed Q/A content, and store them in a local Chroma collection."
    )
    if st.button("(Re)build KB from TESDA FAQ pages"):
        st.session_state.rebuild = True

# --------------------------
# Chroma + Embedding setup
# --------------------------
@st.cache_resource
def get_chroma_client():
    # local persistence in ./chroma_db
    client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        )
    )
    return client

client = get_chroma_client()

@st.cache_resource
def get_sentence_transformer():
    # Provides embeddings to Chroma
    return SentenceTransformer("all-MiniLM-L6-v2")

st.write("Embedding model: all-MiniLM-L6-v2")

embedder = get_sentence_transformer()

# Create Chroma embedding function wrapper for SentenceTransformer
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    model=embedder
)

COLLECTION_NAME = "tesda_faqs"

def ensure_collection():
    # Create or get collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn
        )
    return collection

collection = ensure_collection()

# --------------------------
# Pages to scrape (seed)
# --------------------------
TESDA_PAGES = [
    "https://www.tesda.gov.ph/About/Tesda/127",  # Assessment and certification FAQs page
    "https://e-tesda.gov.ph/local/staticpage/view.php?page=FAQ",
    "https://www.tesda.gov.ph/About/TESDA/25687",  # Scholarship FAQs
    "https://knowledgebase-bsrs.tesda.gov.ph/",    # BSRS knowledge base (faq mirror)
]

# --------------------------
# Scraping helpers
# --------------------------
def fetch_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
    except Exception as e:
        st.warning(f"Failed to fetch {url}: {e}")
        return ""
    soup = BeautifulSoup(r.text, "html.parser")

    # Try to get FAQ style Q/A blocks first
    # Heuristics: look for <h2/h3> for questions and <p> for answers
    texts = []
    # collect FAQ-like items
    for qa in soup.select("div.faq, .faq, .faq-item, .question, .faq_list, .panel, .article"):
        texts.append(qa.get_text(separator="\n").strip())

    # fallback: pull main content
    if not texts:
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            texts.append(main.get_text(separator="\n").strip())
        else:
            texts.append(soup.get_text(separator="\n").strip())

    return "\n\n".join(texts)

def chunk_text(text: str, max_chars=1000) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    cur = ""
    for p in paragraphs:
        if len(cur) + len(p) + 1 > max_chars:
            chunks.append(cur.strip())
            cur = p
        else:
            cur = cur + "\n" + p
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def build_kb_from_seed(pages: List[str]):
    col = ensure_collection()
    # clear existing
    try:
        col.delete()
        col = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    except Exception:
        col = ensure_collection()

    docs = []
    metadatas = []
    ids = []
    for url in pages:
        st.info(f"Fetching {url}")
        text = fetch_text_from_url(url)
        if not text:
            continue
        chunks = chunk_text(text, max_chars=800)
        for i, c in enumerate(chunks):
            docs.append(c)
            metadatas.append({"source": url, "chunk": i})
            ids.append(f"{os.path.basename(url)}_{i}")
    if docs:
        col.add(documents=docs, metadatas=metadatas, ids=ids)
        client.persist()
        st.success(f"Added {len(docs)} document chunks to Chroma.")
    else:
        st.warning("No documents were added. Check the seed URLs or your network.")

# Rebuild if user clicked
if st.session_state.get("rebuild", False):
    build_kb_from_seed(TESDA_PAGES)
    st.session_state.rebuild = False

# On first run, ensure we have some documents (but don't auto-scrape every run)
if client.get_collection(name=COLLECTION_NAME).count() == 0:
    st.info("Knowledge base appears empty. Click the button on the right to (Re)build using TESDA FAQ pages.")

# --------------------------
# Retrieval + Generation
# --------------------------
def retrieve_docs(query: str, k: int = 4):
    col = ensure_collection()
    # semantic search via Chroma
    results = col.query(query_texts=[query], n_results=k, include=["documents", "metadatas"])
    docs = []
    if results and "documents" in results:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        # attach metadata inline
        combined = []
        for d, m in zip(docs, metas):
            src = m.get("source", "unknown")
            combined.append({"text": d, "source": src})
        return combined
    return []

def build_prompt(question: str, retrieved: List[dict]) -> str:
    context_blocks = []
    for r in retrieved:
        snippet = r["text"]
        src = r.get("source", "unknown")
        context_blocks.append(f"Source: {src}\n{snippet}\n---")
    context = "\n\n".join(context_blocks) if context_blocks else "No contextual documents found."
    prompt = f"""You are a friendly customer support assistant. Use the context below (from TESDA FAQs and pages) to answer the user's question.\n\nContext:\n{context}\n\nUser question:\n{question}\n\nAnswer concisely. If the answer is not present in the context, be honest and say you don't know and offer general guidance on how to get the official answer (e.g., contact TESDA or point to the TESDA website). When referencing facts from the context, mention the source URL.\n\nAnswer:"""
    return prompt

def azure_chat_completion(prompt: str, max_tokens: int = 400) -> str:
    # uses Azure OpenAI ChatCompletion API
    resp = openai.ChatCompletion.create(
        engine=AZURE_DEPLOYMENT_NAME,  # your deployment name
        messages=[
            {"role": "system", "content": "You are a helpful customer support assistant specialized in TESDA FAQs."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=max_tokens,
    )
    return resp["choices"][0]["message"]["content"]

# --------------------------
# User interaction
# --------------------------
st.markdown("### Ask a question about TESDA (training, assessment, scholarships, TOP, etc.)")
q = st.text_input("Your question", key="question_input")
col1, col2 = st.columns([1, 3])
with col1:
    top_k = st.number_input("Number of retrieved docs", min_value=1, max_value=8, value=4)
    if st.button("Answer"):
        if not q.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Retrieving relevant FAQ content..."):
                retrieved = retrieve_docs(q, k=top_k)
            if not retrieved:
                st.info("No matching TESDA FAQ text found in KB. You may want to (Re)build the KB from TESDA pages.")
            # show retrieved snippets
            with st.expander("Retrieved context snippets"):
                for i, r in enumerate(retrieved):
                    st.markdown(f"**Snippet {i+1} — Source:** {r['source']}")
                    st.write(textwrap.shorten(r["text"], width=800, placeholder="..."))
            prompt = build_prompt(q, retrieved)
            with st.spinner("Calling Azure OpenAI..."):
                try:
                    answer = azure_chat_completion(prompt)
                    st.markdown("### ✅ Answer")
                    st.write(answer)
                except Exception as e:
                    st.error(f"OpenAI call failed: {e}")
