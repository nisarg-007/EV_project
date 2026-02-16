# Project Setup Guide

This guide provides step-by-step instructions to set up the development environment for the **EV Infrastructure & Policy Intelligence System**.

## Prerequisites

Before starting, ensure you have the following installed:

1.  **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
2.  **Ollama**: [Download Ollama](https://ollama.com/) (Required for local LLM inference)
3.  **Git**: [Download Git](https://git-scm.com/downloads)

## 1. Environment Setup

### 1.1 Clone the Repository
```bash
git clone <repository_url>
cd AI
```

### 1.2 Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 1.3 Install Dependencies
Install all required Python packages.

```bash
pip install -r scripts/requirements.txt
```

## 2. Configuration (`.env`)

You need to set up environment variables for the application to function correctly.

1.  Navigate to the `scripts` directory (or root, depending on where your `.env` is expected, typically root for project-wide access, but `setup_rag.py` checks current env).
    *   *Note: The current `setup_rag.py` loads `.env` relative to its execution or from the current working directory.*
2.  Create a `.env` file in the `scripts/` directory (or root if you prefer to run from root):

```bash
touch scripts/.env
```

3.  Add the following variables to `scripts/.env`:

```env
# Pinecone Vector Database Config
PINECONE_API_KEY=your_pinecone_api_key_here

# (Optional) Ollama Config if running on a custom host
# OLLAMA_HOST=http://localhost:11434
```

> **Get a Pinecone API Key:**
> 1. Sign up at [Pinecone.io](https://www.pinecone.io/).
> 2. Create a new "Serverless" index (or wait for the script to do it).
> 3. Copy your API Key.

## 3. Ollama Setup (Local LLM)

1.  **Start Ollama**: Ensure the Ollama app is running in the background.
2.  **Pull the Embedding Model**:
    The system uses `nomic-embed-text` for embeddings. Run this command in your terminal:

    ```bash
    ollama pull nomic-embed-text
    ```

3.  **Pull the LLM (Optional for now, required later):**
    ```bash
    ollama pull llama3
    ```

## 4. Running the RAG Setup Pipeline

This script will initialize the Vector Database and ingest the project documentation.

1.  Ensure you are in the `scripts` directory or run from root pointing to it.
2.  Run the setup script:

```bash
cd scripts
python setup_rag.py
```

**What this script does:**
*   Connects to Pinecone.
*   Creates the index `ev-policy-docs` if it doesn't exist.
*   Reads `../docs/EV_Project_Plan.pdf`.
*   Chunks the text.
*   Generates embeddings using local Ollama model.
*   Upserts vectors to Pinecone.

## 5. Verification

If the script runs successfully, you should see output indicating:
*   "Connected to Pinecone Index..."
*   "Found X text chunks..."
*   "Successfully upserted X chunks..."

You are now ready to proceed with development!
