# AI SYSTEM PROMPT: EV POLICY RAG PIPELINE (PARVA)

**Role:** Senior AI/ML Engineer (RAG Specialist)
**Objective:** Finalize the Retrieval-Augmented Generation (RAG) pipeline for the EV Intelligence Platform.

## 📁 REPOSITORY CONTEXT
- **Repo Path:** `EV_project/`
- **Data Location:** `data/policy/` (contains `.md` policy fact sheets) and `data/raw/` (contains `.pdf` documents).
- **Existing Script:** `scripts/setup_rag.py` (needs upgrade).
- **Target Module:** `scripts/rag_query.py` (needs to be created).

## 🛠️ TECHNICAL STACK
- **Orchestration:** Python, LangChain
- **Vector DB:** Pinecone (Serverless)
- **Embeddings:** Ollama (Model: `nomic-embed-text`, 768 dimensions)
- **LLM:** Ollama (Model: `llama3.2`)

## 📋 TASKS FOR THE AI
1. **Upgrade `scripts/setup_rag.py`**:
   - Must loop through ALL files in `data/policy/` (markdown) and `data/raw/` (PDFs).
   - Use `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=50).
   - Store metadata: `source` (filename), `page_number` (if PDF), and `text`.
   - Ensure Pinecone upsert logic handles multiple files without ID collisions.
2. **Create `scripts/rag_query.py`**:
   - Implement `query_policy_docs(question: str, top_k: int = 5)`.
   - Function must return a list of dictionaries with `text`, `source`, and `score`.
   - Include a CLI test block at the bottom of the script.

## ⚠️ CONSTRAINTS
- **Local First:** Do NOT use OpenAI or Anthropic APIs for embeddings. Use Ollama.
- **Paths:** Use relative paths from the script location.
- **Robustness:** Add error handling for empty files or failed Pinecone connections.

---
**INSTRUCTION:** "I am working as Parva. Please read the current `scripts/setup_rag.py`, then generate the full updated code for it and the new `scripts/rag_query.py` to complete the RAG pipeline."
