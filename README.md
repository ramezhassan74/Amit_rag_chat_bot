# AMIT RAG Chatbot

## Overview
AMIT RAG Chatbot is a Retrieval-Augmented Generation (RAG) project powered by Google's Gemini API.  
It allows you to upload and ingest PDF documents, split them into text chunks, and retrieve the most relevant context to answer your questions accurately.

## Features
- PDF ingestion using `pdfplumber`.
- Text chunking for better retrieval.
- Vector search with FAISS (or other DBs).
- Gemini API for generating context-aware answers.
- Interactive Gradio UI.

## Tech Stack
- Python
- pdfplumber
- FAISS
- Gradio
- Gemini API

## How it Works
1. Ingest and chunk PDFs from `docs/`.
2. Convert chunks into embeddings and store in FAISS.
3. When a user asks a question:
   - Embed the query.
   - Retrieve top chunks.
   - Build prompt with context + instructions.
   - Send to Gemini API for the final answer.

## Run Locally
```bash


# AMIT RAG Chatbot

## نظرة عامة
AMIT RAG Chatbot هو مشروع بيعتمد على مفهوم **التوليد المعزز بالاسترجاع (RAG)** باستخدام Google Gemini API.  
فكرته إنك ترفع ملفات PDF، والبوت يقرأها ويقسمها لقطع صغيرة، وبعدها يسترجع أهم المعلومات علشان يجاوبك بدقة وسياق صحيح.

## المميزات
- قراءة ملفات PDF بسهولة باستخدام `pdfplumber`.
- تقسيم النصوص (chunking) لسهولة المعالجة.
- البحث السريع باستخدام FAISS أو أي قاعدة بيانات مشابهة.
- إجابات ذكية ودقيقة من Gemini API.
- واجهة محادثة تفاعلية بـ Gradio.

## التقنيات
- Python 🐍
- pdfplumber 📄
- FAISS 🔎
- Gradio 💬
- Gemini API 🤖

## طريقة العمل
1. تحميل ملفات PDF من مجلد `docs/`.
2. تقسيم النصوص لقطع صغيرة وتحويلها إلى embeddings.
3. عند كتابة سؤال:
   - تحويل السؤال لـ embedding.
   - استرجاع أنسب المقاطع.
   - بناء برومبت بالسياق + التعليمات.
   - إرسال للـ Gemini API لتوليد الإجابة النهائية.

## طريقة التشغيل محليًا
```bash
git clone https://github.com/ramezhassan74/Amit_rag_chat_bot.git
cd Amit_rag_chat_bot
pip install -r requirements.txt
python backend.py
