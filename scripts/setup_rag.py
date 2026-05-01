import os
import time
import hashlib
import ollama
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

SCRIPT_DIR_EARLY = os.path.dirname(os.path.abspath(__file__))
load_dotenv()
# Try specific locations if default fails
if not os.getenv("PINECONE_API_KEY"):
    load_dotenv(os.path.join(SCRIPT_DIR_EARLY, '..', '.env'))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'policy')
RAW_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'raw')
INDEX_NAME = "ev-policy-docs"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_DIMENSION = 768


def get_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise EnvironmentError("PINECONE_API_KEY not found in environment.")

    pc = Pinecone(api_key=api_key)

    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index: {INDEX_NAME}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(2)

    index = pc.Index(INDEX_NAME)
    print(f"Connected to Pinecone index: {INDEX_NAME}")
    return index


def stable_chunk_id(source: str, chunk_index: int) -> str:
    """Generate a collision-safe ID from filename + chunk index."""
    key = f"{source}::{chunk_index}"
    return hashlib.md5(key.encode()).hexdigest()


def load_markdown_chunks(splitter: RecursiveCharacterTextSplitter) -> list[dict]:
    """Read all .md files from data/policy/ and return chunk dicts."""
    chunks = []
    policy_dir = os.path.realpath(POLICY_DIR)
    if not os.path.isdir(policy_dir):
        print(f"Warning: policy directory not found: {policy_dir}")
        return chunks

    for filename in sorted(os.listdir(policy_dir)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(policy_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            if not text:
                print(f"Skipping empty file: {filename}")
                continue
            for i, chunk in enumerate(splitter.split_text(text)):
                chunks.append({
                    "id": stable_chunk_id(filename, i),
                    "text": chunk,
                    "source": filename,
                    "page_number": None,
                })
            print(f"  Loaded {filename}: {i + 1} chunks")
        except Exception as e:
            print(f"  Error reading {filename}: {e}")

    return chunks


def load_pdf_chunks(splitter: RecursiveCharacterTextSplitter) -> list[dict]:
    """Read all .pdf files from data/raw/ and return chunk dicts."""
    chunks = []
    raw_dir = os.path.realpath(RAW_DIR)
    if not os.path.isdir(raw_dir):
        print(f"Warning: raw directory not found: {raw_dir}")
        return chunks

    for filename in sorted(os.listdir(raw_dir)):
        if not filename.lower().endswith('.pdf'):
            continue
        filepath = os.path.join(raw_dir, filename)
        try:
            reader = PdfReader(filepath)
            if not reader.pages:
                print(f"Skipping empty PDF: {filename}")
                continue

            chunk_index = 0
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if not page_text:
                    continue
                for chunk in splitter.split_text(page_text):
                    chunks.append({
                        "id": stable_chunk_id(filename, chunk_index),
                        "text": chunk,
                        "source": filename,
                        "page_number": page_num,
                    })
                    chunk_index += 1
            print(f"  Loaded {filename}: {chunk_index} chunks")
        except Exception as e:
            print(f"  Error reading {filename}: {e}")

    return chunks


def embed_and_upsert(index, chunks: list[dict], batch_size: int = 5):
    """Embed each chunk with Ollama and upsert to Pinecone in batches."""
    vectors = []
    # Configure ollama client if OLLAMA_BASE_URL is set
    client = ollama.Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    print(f"  Starting embedding for {len(chunks)} chunks...")
    for i, chunk_meta in enumerate(chunks):
        try:
            print(f"    [{i+1}/{len(chunks)}] Embedding chunk from {chunk_meta['source']}...", end="\r")
            response = client.embeddings(model=EMBEDDING_MODEL, prompt=chunk_meta["text"])
            embedding = response["embedding"]
            
            # Sanitize text for Pinecone metadata (avoid encoding errors)
            # We replace common problematic characters first, then strip anything else non-ASCII
            safe_text = chunk_meta["text"].replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '-').replace('\u2014', '-').replace('\u2022', '*')
            safe_text = safe_text.encode('ascii', 'ignore').decode('ascii')
            
            metadata = {
                "text": safe_text,
                "source": chunk_meta["source"],
            }
            if chunk_meta["page_number"] is not None:
                metadata["page_number"] = chunk_meta["page_number"]

            vectors.append({
                "id": chunk_meta["id"],
                "values": embedding,
                "metadata": metadata,
            })
        except Exception as e:
            print(f"\n  Embedding error for chunk {chunk_meta['id']} ({chunk_meta['source']}): {e}")

    print(f"\n  Embedding complete. Upserting {len(vectors)} vectors in batches of {batch_size}...")
    if not vectors:
        print("No vectors to upsert.")
        return

    for start in range(0, len(vectors), batch_size):
        batch = vectors[start:start + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"    Upserted batch {start // batch_size + 1}/{ (len(vectors)-1)//batch_size + 1}")
        except Exception as e:
            print(f"  Pinecone upsert error: {e}")

    print(f"Total vectors in batch process: {len(vectors)}")


def setup_pinecone_rag():
    try:
        index = get_pinecone_index()
    except EnvironmentError as e:
        print(f"Error: {e}")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    print("\nLoading markdown policy files...")
    md_chunks = load_markdown_chunks(splitter)

    print("\nLoading raw PDF files...")
    pdf_chunks = load_pdf_chunks(splitter)

    all_chunks = md_chunks + pdf_chunks
    print(f"\nTotal chunks to embed: {len(all_chunks)}")

    if not all_chunks:
        print("No documents found. Check data/policy/ and data/raw/ directories.")
        return

    print("\nEmbedding and upserting to Pinecone...")
    embed_and_upsert(index, all_chunks)
    print("\nRAG setup complete.")


if __name__ == "__main__":
    setup_pinecone_rag()
