import os
import pdfplumber   # مكتبة قوية للتعامل مع PDF
import gradio as gr

# حط المسار الكامل للـ docs
DOCS_DIR = r"D:\Chatbot\AMIT_RAG_Chatbot\docs"

def read_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # يتأكد إن الصفحة مش فاضية
                    text += page_text + "\n"
    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")
    return text


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def ingest_docs():
    all_chunks = []

    if not os.path.exists(DOCS_DIR):
        print(f"❌ Directory not found: {DOCS_DIR}")
        return []

    docs_files = os.listdir(DOCS_DIR)

    for file in docs_files:
        path = os.path.join(DOCS_DIR, file)
        text = ""

        if file.lower().endswith(".pdf"):
            print(f"📄 Processing: {file}")
            text = read_pdf(path)
            if text:
                chunks = chunk_text(text)
                all_chunks.extend(chunks)

    print(f"✅ Loaded {len(all_chunks)} chunks from {len(docs_files)} files (PDF only)")
    return all_chunks


if __name__ == "__main__":
    chunks = ingest_docs()
    print(chunks[:2])

    