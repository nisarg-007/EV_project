"""
rag_query.py — LangChain-orchestrated RAG query module for EV Policy docs.

Orchestration stack:
  Embeddings : OllamaEmbeddings  (nomic-embed-text, 768-dim)
  Vector DB  : PineconeVectorStore (ev-policy-docs index)
  LLM        : ChatOllama          (llama3.2)
  Chain      : LangChain LCEL      (retriever | prompt | llm | parser)
"""

import os
import sys

from dotenv import load_dotenv

# ── LangChain core ────────────────────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ── LangChain integrations ────────────────────────────────────────────────────
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_pinecone import PineconeVectorStore

# ── Environment ───────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_SCRIPT_DIR, '..', '.env'))

INDEX_NAME      = "ev-policy-docs"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL       = "llama3.2"


# ── Shared helpers ────────────────────────────────────────────────────────────

def _get_embeddings() -> OllamaEmbeddings:
    """Return a configured OllamaEmbeddings instance."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url="http://127.0.0.1:11434")


def _get_vectorstore() -> PineconeVectorStore:
    """
    Connect to the existing Pinecone index via LangChain's PineconeVectorStore.
    Raises EnvironmentError if PINECONE_API_KEY is missing.
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise EnvironmentError("PINECONE_API_KEY not found in environment.")

    return PineconeVectorStore(
        index_name=INDEX_NAME,
        embedding=_get_embeddings(),
        pinecone_api_key=api_key,
        text_key="text",          # matches the metadata key used in setup_rag.py
    )


# ── Public API ────────────────────────────────────────────────────────────────

def query_policy_docs(question: str, top_k: int = 5) -> list[dict]:
    """
    Retrieve the most relevant policy chunks for *question* using
    LangChain's PineconeVectorStore similarity search.

    Returns
    -------
    list[dict]  — each dict has keys:
        text   : str   – raw chunk text
        source : str   – originating filename
        score  : float – cosine similarity score (0–1)
    """
    if not question.strip():
        return []

    try:
        vectorstore = _get_vectorstore()
    except EnvironmentError as e:
        print(f"Connection error: {e}")
        return []

    try:
        # similarity_search_with_score returns (Document, score) tuples
        results = vectorstore.similarity_search_with_score(question, k=top_k)
    except Exception as e:
        print(f"Retrieval error: {e}")
        return []

    return [
        {
            "text":   doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score":  round(float(score), 4),
        }
        for doc, score in results
    ]


def answer_with_rag(question: str, top_k: int = 5) -> str:
    """
    Full RAG pipeline using a LangChain LCEL chain:
      retriever → context formatter → ChatPromptTemplate → ChatOllama → StrOutputParser

    Parameters
    ----------
    question : str  – natural-language question about EV policy
    top_k    : int  – number of chunks to retrieve (default 5)

    Returns
    -------
    str – generated answer grounded in retrieved policy documents
    """
    if not question.strip():
        return "Please provide a question."

    try:
        vectorstore = _get_vectorstore()
    except EnvironmentError as e:
        return f"Connection error: {e}"

    # ── Build LCEL chain ──────────────────────────────────────────────────────
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    llm       = ChatOllama(model=LLM_MODEL, base_url="http://127.0.0.1:11434")

    prompt = ChatPromptTemplate.from_template(
        "You are an expert on EV policy. Answer the question using ONLY the "
        "context below. If the context does not contain enough information, "
        "say so clearly.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    def _format_docs(docs) -> str:
        """Concatenate retrieved docs into a single context string."""
        return "\n\n---\n\n".join(
            f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )

    # LCEL pipeline: retriever feeds context; question passes through unchanged
    chain = (
        {
            "context":  retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        return chain.invoke(question)
    except Exception as e:
        return f"RAG chain error: {e}"


# ── CLI test block ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What EV tax credits are available under the Inflation Reduction Act?"
    )

    print(f"\nQuestion: {question}\n")

    # ── Step 1: raw retrieval results ─────────────────────────────────────────
    print("=== Retrieved Chunks (LangChain PineconeVectorStore) ===")
    results = query_policy_docs(question)
    if not results:
        print("No results returned.")
    else:
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] Source: {r['source']}  |  Score: {r['score']}")
            print(r["text"][:300] + ("..." if len(r["text"]) > 300 else ""))

    # ── Step 2: generated answer via LCEL RAG chain ───────────────────────────
    print("\n=== Generated Answer (LangChain LCEL RAG Chain) ===")
    print(answer_with_rag(question))
