# Setup Guide — EV Intelligence Platform

## Prerequisites
- Python 3.10+ installed
- Git installed
- 8GB+ RAM recommended (for Ollama)

## Step 1: Clone the Repository
```bash
git clone https://github.com/somildoshi12/EV_project.git
cd EV_project
```

## Step 2: Install Python Dependencies
```bash
pip install -r scripts/requirements.txt
```

## Step 3: Install Ollama (Local LLM)
- Download from: https://ollama.com/download
- After install, pull the required models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Step 4: Set Up Pinecone (Vector DB)
1. Create a free account at https://www.pinecone.io/
2. Get your API key from the Pinecone dashboard
3. Create a `.env` file in the project root:
```
PINECONE_API_KEY=your_key_here
```

## Step 5: Populate the RAG Database
```bash
cd scripts
python setup_rag.py
```

## Step 6: Run the Application
```bash
cd ..
streamlit run app.py
```
The app will open at http://localhost:8501
