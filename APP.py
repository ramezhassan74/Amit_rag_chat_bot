# backend.py
import os
import PyPDF2
import requests
from prompting import prompt_config   # ملف البرومبت بتاعك
import time
import logging
import hashlib
from typing import Dict

# ======================
#   إعدادات Gemini API
# ======================
API_KEY = "AIzaSyCmyBnUkNvm70VpbJLLvIaFdv6YB7t2JwA"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

DOCS_DIR = r"D:\Chatbot\AMIT_RAG_Chatbot\AMIT_RAG_Chatbot\docs"


# ======================
#   Cache Layer
# ======================
class SimpleCache:
    def __init__(self):
        self.cache: Dict[str, str] = {}

    def _hash(self, query: str) -> str:
        return hashlib.md5(query.lower().encode()).hexdigest()

    def get(self, query: str):
        key = self._hash(query)
        return self.cache.get(key)

    def set(self, query: str, response: str):
        key = self._hash(query)
        self.cache[key] = response


cache = SimpleCache()


# ======================
#   قراءة الـ PDF
# ======================
def read_all_pdfs(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            try:
                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            all_text += text + "\n"
                print(f"📄 Loaded: {filename}")
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
    return all_text


# ---- تحميل المعرفة مرة واحدة ----
relevant_context = read_all_pdfs(DOCS_DIR)

if not relevant_context.strip():
    raise ValueError("❌ No information found in PDFs. Please check docs folder.")


# ======================
#   Wrapper Function
# ======================
def gemini_chat_wrapper(message, history=[]):
    # 🔍 أولاً: نشوف لو الرد متخزن في الكاش
    cached = cache.get(message)
    if cached:
        return f" {cached}"

    # بناء البرومبت
    final_prompt = f"""
{prompt_config['instructions']}

CONTEXT:
{relevant_context}

QUESTION:
{message}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": final_prompt},
                ]
            }
        ]
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        try:
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            # نخزن النتيجة في الكاش قبل ما نرجعها
            cache.set(message, answer)
            return answer
        except Exception as e:
            return f"⚠️ Unexpected response format: {e}\n{data}"
    else:
        return f"❌ Error: {response.status_code} - {response.text}"


# ======================
#   Logging
# ======================
logging.basicConfig(level=logging.INFO)

start = time.time()
# مثال: استدعاء مرة للتجربة
# print(gemini_chat_wrapper("What is AI?"))
end = time.time()

logging.info(f"Execution time: {end - start:.2f} seconds")