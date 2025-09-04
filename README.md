# AMIT RAG Chatbot

## Overview
AMIT RAG Chatbot is a Retrieval-Augmented Generation project built with Google Gemini API.  
It processes PDF documents, splits them into chunks, retrieves relevant knowledge, and generates accurate answers through a Gradio interface.

## Features
- Reads and processes PDFs with `pdfplumber`
- Chunks text for efficient retrieval
- Embedding & similarity search (FAISS or similar DB)
- Smart context-aware answers using Gemini API
- Interactive chat with Gradio UI

## Tech Stack
- Python 🐍  
- pdfplumber 📄  
- FAISS 🔎  
- Gradio 💬  
- Gemini API 🤖  

## How It Works
1. Load PDFs from `docs/` folder  
2. Chunk text & generate embeddings  
3. On each user query:
   - Convert question to embedding  
   - Retrieve the most relevant chunks  
   - Build prompt with context & instructions  
   - Send to Gemini API for the final answer  

## Run Locally
```bash
git clone https://github.com/ramezhassan74/Amit_rag_chat_bot.git
cd Amit_rag_chat_bot
pip install -r requirements.txt
python backend.py




