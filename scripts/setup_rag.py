import os
import time
import ollama
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Configuration
DOCS_DIR = '../docs'
INDEX_NAME = "ev-policy-docs"
EMBEDDING_MODEL = "nomic-embed-text" # Default robust local model
VECTOR_DIMENSION = 768 # nomic-embed-text outputs 768 dimensions

def setup_pinecone_rag():
    # 1. Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("Error: PINECONE_API_KEY not found in environment.")
        return

    pc = Pinecone(api_key=api_key)

    # 2. Check/Create Index
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating index: {INDEX_NAME}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=VECTOR_DIMENSION, 
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        time.sleep(1) 

    index = pc.Index(INDEX_NAME)
    print(f"Connected to Pinecone Index: {INDEX_NAME}")

    # 3. Process & Embed Document
    pdf_path = os.path.join(DOCS_DIR, 'EV_Project_Plan.pdf')
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Robust Chunking using LangChain
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        print(f"Found {len(chunks)} text chunks to embed.")
        
        vectors = []
        for i, chunk in enumerate(chunks):
            try:
                # Generate Embedding using Ollama
                response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=chunk)
                embedding = response["embedding"]
                
                vectors.append({
                    "id": f"plan_chunk_{i}",
                    "values": embedding,
                    "metadata": {"text": chunk, "source": "EV_Project_Plan.pdf"}
                })
            except Exception as e:
                print(f"Error embedding chunk {i}: {e}")

        # 4. Upsert to Pinecone
        if vectors:
            index.upsert(vectors=vectors)
            print(f"Successfully upserted {len(vectors)} chunks to Pinecone.")
    else:
        print(f"Document not found at: {pdf_path}")

if __name__ == "__main__":
    setup_pinecone_rag()
