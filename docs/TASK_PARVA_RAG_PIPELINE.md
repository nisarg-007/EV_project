# 🤖 PARVA — Policy Collection & RAG Pipeline

**Role:** RAG / Knowledge Engineer  
**Branch Name:** `parva`  
**Estimated Time:** 10-12 hours

---

## 🚨 FILE RESTRICTIONS — READ CAREFULLY

### ✅ Files you CAN create/edit:
```
scripts/setup_rag.py            ← Modify to process multiple PDFs (EDIT)
scripts/rag_query.py            ← Query function for RAG retrieval (CREATE)
data/raw/                       ← Download policy PDFs here (ADD FILES)
  data/raw/wa_state_ev_laws.pdf
  data/raw/nevi_program_guidance.pdf
  data/raw/ira_ev_tax_credits.pdf
  data/raw/wa_rcw_82_08_809.pdf
  data/raw/afdc_wa_incentives.pdf
.env                            ← Pinecone API key (CREATE if not exists)
```

### 🚫 Files you MUST NOT edit:
```
app.py, pages/                  ← Somil owns this
scripts/analytics_tools.py      ← Nisarg owns this
scripts/agent_workflow.py       ← MD owns this
tests/                          ← Smit owns this
notebooks/                      ← Nisarg owns this
data/processed/                 ← Nisarg owns this
```

---

## 📋 TASK DESCRIPTION

You are the **knowledge pipeline** of this project. Your job is to:

1. **Find and download** real EV policy documents (PDFs) from government sources
2. **Modify `setup_rag.py`** to process ALL PDFs in the `data/raw/` folder (not just one)
3. **Populate the Pinecone vector database** with embedded policy chunks
4. **Create a query function** that retrieves relevant policy context for a given question
5. **Verify** that the RAG retrieval returns meaningful, correct results

---

## 🎯 MINIMUM BENCHMARKS (Must achieve ALL)

### Benchmark 1: At least 5 policy PDFs downloaded
- [ ] Place them in `data/raw/` folder
- [ ] Each PDF must be a REAL government/official document (not made up)
- [ ] Total pages across all PDFs: at least 50 pages

### Benchmark 2: setup_rag.py processes all PDFs
```bash
cd EV_project/scripts
python setup_rag.py
# Must output: "Processing 5 PDFs..." and "Successfully upserted X chunks"
```
- [ ] Loops through ALL `.pdf` files in `data/raw/`
- [ ] Each chunk stores metadata: `source` (filename), `page_number`, `text`
- [ ] Uses `RecursiveCharacterTextSplitter` with chunk_size=500, overlap=50
- [ ] Handles errors gracefully (doesn't crash on bad PDF)

### Benchmark 3: rag_query.py returns relevant results
```bash
cd EV_project/scripts
python rag_query.py "Is a Tesla Model Y eligible for CAFV credit in Washington?"
# Must return top 3 relevant chunks with source and text
```
- [ ] Takes a query string, embeds it using Ollama
- [ ] Queries Pinecone for top-K similar chunks (K=5)
- [ ] Returns results as a list of dicts with `text`, `source`, `score`
- [ ] Results are actually relevant to the query (not random garbage)

### Benchmark 4: Pinecone index is populated
- [ ] At least 200 chunks in the index
- [ ] Chunks are searchable and return meaningful similarity scores (>0.5)

---

## 🏗️ STEP-BY-STEP INSTRUCTIONS

### Step 1: Download policy documents

Save each as a PDF in `data/raw/`:

| Document | How to Get It |
|:---|:---|
| **WA State EV Laws Summary** | Go to https://afdc.energy.gov/laws/state_summary?state=WA → Print page as PDF |
| **NEVI Program Guidance** | Search "NEVI formula program guidance PDF" on fhwa.dot.gov |
| **IRA EV Tax Credit Rules** | Search "IRS clean vehicle credit fact sheet PDF" on irs.gov |
| **WA RCW 82.08.809** | Go to https://app.leg.wa.gov/rcw/default.aspx?cite=82.08.809 → Print as PDF |
| **AFDC WA Incentives** | Go to https://afdc.energy.gov/laws/state_summary?state=WA → Save the detailed page |

You may also add any other relevant policy PDFs you find. More documents = better RAG.

### Step 2: Update setup_rag.py to handle multiple PDFs

Replace the single-file processing with a loop:

```python
import glob

# Find all PDFs in data/raw/
pdf_files = glob.glob(os.path.join(DOCS_DIR, '../data/raw/*.pdf'))
print(f"Found {len(pdf_files)} PDF files to process.")

for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    print(f"\nProcessing: {filename}")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    chunks = text_splitter.split_text(text)
    print(f"  → {len(chunks)} chunks extracted")
    
    for i, chunk in enumerate(chunks):
        # Use filename in the chunk ID to avoid collisions
        chunk_id = f"{filename}_chunk_{i}"
        # ... embed and upsert
```

### Step 3: Create `scripts/rag_query.py`

```python
"""
RAG Query Module — retrieves relevant policy context from Pinecone.
Person 4 will import this: from scripts.rag_query import query_policy_docs
"""

import os
import ollama
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "ev-policy-docs"
EMBEDDING_MODEL = "nomic-embed-text"

def query_policy_docs(question: str, top_k: int = 5) -> list[dict]:
    """
    Embed a question and retrieve the most relevant policy chunks.
    
    Returns: list of {"text": str, "source": str, "score": float}
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(INDEX_NAME)
    
    # Embed the question
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=question)
    query_embedding = response["embedding"]
    
    # Query Pinecone
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    
    return [
        {
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", "unknown"),
            "score": match.score
        }
        for match in results.matches
    ]

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What EV incentives are available in Washington state?"
    print(f"\nQuery: {query}\n")
    results = query_policy_docs(query)
    for i, r in enumerate(results):
        print(f"--- Result {i+1} (score: {r['score']:.4f}) ---")
        print(f"Source: {r['source']}")
        print(f"Text: {r['text'][:300]}...")
        print()
```

### Step 4: Set up .env file
```
PINECONE_API_KEY=your_actual_key_here
```
Make sure `.env` is in `.gitignore` (it already is).

### Step 5: Prerequisites
```bash
# Must have Ollama running locally with the embedding model:
ollama pull nomic-embed-text
# Verify it works:
ollama run nomic-embed-text "test"
```

---

## 📦 DELIVERABLE CHECKLIST

```
[ ] At least 5 real PDF files in data/raw/
[ ] setup_rag.py processes ALL PDFs in data/raw/ (not hardcoded filename)
[ ] python scripts/setup_rag.py completes without error
[ ] Pinecone index has 200+ chunks
[ ] scripts/rag_query.py exists and is importable
[ ] python scripts/rag_query.py "test question" returns relevant results
[ ] Each chunk has metadata: text, source filename
[ ] Error handling: bad PDFs don't crash the script
[ ] .env file has PINECONE_API_KEY (not committed to Git)
[ ] Ollama nomic-embed-text model is installed and working
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't use OpenAI embeddings** — We use Ollama (local, free). The model is `nomic-embed-text`.
2. **Don't commit `.env` to Git** — The API key is secret. It's already in `.gitignore`.
3. **Don't use chunk IDs like `chunk_0`, `chunk_1`** — If you process multiple PDFs, IDs will collide. Use `{filename}_chunk_{i}`.
4. **Don't skip bad PDFs** — Some PDFs have images only (no extractable text). Handle this gracefully with try/except.
5. **Don't process huge PDFs** — If a PDF is 500+ pages, consider processing only relevant sections.
