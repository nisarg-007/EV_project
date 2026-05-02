#!/bin/bash

# EV Project Automated Setup Script
# This script automates the environment setup for new teammates.

echo "🚀 Starting EV Project Setup..."

# 1. Check for Prerequisites
command -v git >/dev/null 2>&1 || { echo "❌ Git is not installed. Please install it first."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker Desktop first."; exit 1; }

# 2. Setup Environment File
if [ ! -f .env ]; then
    echo "📄 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Action Required: Please open the .env file and add your PINECONE_API_KEY."
    echo "   Once you've added the key, run this script again."
    exit 1
else
    # Check if PINECONE_API_KEY is still default or empty
    if grep -q "PINECONE_API_KEY=\"\"" .env || grep -q "PINECONE_API_KEY=your_key_here" .env; then
        echo "⚠️  Action Required: Your PINECONE_API_KEY is not set in the .env file."
        exit 1
    fi
fi

# 3. Start Docker Containers
echo "🐳 Starting Docker containers (this may take a few minutes)..."
docker compose up -d --build

# 4. Pull AI Models
echo "🧠 Pulling LLM models (Llama 3.2 and Nomic Embeddings)..."
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull nomic-embed-text

# 5. Initialize Vector Database
echo "📚 Initializing Vector Database (RAG)..."
docker compose exec streamlit python scripts/setup_rag.py

echo "✅ Setup Complete!"
echo "------------------------------------------------"
echo "📊 Dashboard: http://localhost:8501"
echo "🔍 View Logs: docker compose logs -f streamlit"
echo "------------------------------------------------"
