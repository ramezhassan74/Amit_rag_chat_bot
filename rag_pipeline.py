# rag_core.py
import os
from typing import List, Dict, Any
from dataclasses import dataclass

# ===== Embeddings & Vector DB =====
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ===== Gemini =====
import google.generativeai as genai

# ---------- إعدادات عامة ----------
EMB_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PERSIST_DIR = "./chroma_store"
COLLECTION_NAME = "kb"
TOP_K = 5

# ---------- تهيئة التضمين والفهرس ----------
_embedder = SentenceTransformer(EMB_MODEL_NAME)

_chroma = chromadb.Client(Settings(persist_directory=PERSIST_DIR))
_collection = _chroma.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)

def _embed(texts: List[str]) -> List[List[float]]:
    return _embedder.encode(texts, normalize_embeddings=True).tolist()

# ---------- استرجاع السياق ----------
@dataclass
class RetrievedChunk:
    id: str
    text: str
    source: str
    chunk_index: int
    score: float | None = None

def retrieve_context(query: str, k: int = TOP_K) -> List[RetrievedChunk]:
    """يسترجع أفضل K مقاطع من Chroma حسب الاستعلام."""
    q_emb = _embed([query])[0]
    res = _collection.query(query_embeddings=[q_emb], n_results=k, include=["metadatas", "documents", "distances", "ids"])
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    ids = res.get("ids", [[]])[0]
    dists = res.get("distances", [[]])[0]  # cosine distance (أقل = أقرب) حسب الإعداد
    out: List[RetrievedChunk] = []
    for d, m, i, dist in zip(docs, metas, ids, dists):
        out.append(RetrievedChunk(
            id=i,
            text=d,
            source=str(m.get("source", "unknown")),
            chunk_index=int(m.get("chunk_index", -1)),
            score=float(dist) if dist is not None else None
        ))
    return out

# ---------- تهيئة Gemini ----------
def _init_gemini(model_name1: str = "AIzaSyCmyBnUkNvm70VpbJLLvIaFdv6YB7t2JwA") -> genai.GenerativeModel:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY ")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name1)

_SYSTEM_PROMPT = {
  "name": "Amit Helper",
  "role": "Data Science and AI Course Instructor",
  "instructions": "You are Amit Helper, a data science and AI course instructor. Your main goal is to help students with their learning, answer their questions, and provide guidance on topics related to data science, machine learning, artificial intelligence, and programming languages like Python and R. Maintain a professional, knowledgeable, and encouraging tone. Always strive to explain complex concepts in a clear, concise, and easy-to-understand manner. You can use analogies and real-world examples to make topics more relatable. When a student asks a question, first acknowledge their query, then provide a helpful and thorough response. Avoid using informal language or emojis. Your primary function is to educate and support your students' learning journey. All titles and key terms should be in **bold**. For important sections or concepts, provide a comprehensive and in-depth explanation. Break down complex ideas into simple, understandable parts, and offer real-world examples to make them relatable."
}

def _build_context(chunks: List[RetrievedChunk]) -> str:
    lines = []
    for idx, c in enumerate(chunks, start=1):
        lines.append(f"[{idx}] (src={c.source} #{c.chunk_index})\n{c.text}\n")
    return "\n".join(lines)

def call_gemini(question: str, chunks: List[RetrievedChunk], model_name: str = "gemini-1.5-flash") -> str:
    """ينادي Gemini بسياق مرقّم لضمان الاستشهاد بالمصادر."""
    model = _init_gemini(model_name)
    context_block = _build_context(chunks) if chunks else "لا توجد مراجع."
    user_prompt = (
        f"السؤال: {question}\n\n"
        f"المراجع:\n{context_block}\n\n"
        f"التعليمات: جاوب من المراجع فقط. إن لم تكفِ، قل ذلك صراحة."
    )
    # ملاحظة: generate_content يقبل نص بسيط أو قائمة أجزاء. نبقيها نصًا بسيطًا هنا.
    resp = model.generate_content([_SYSTEM_PROMPT, user_prompt])
    return (resp.text or "").strip()

# ---------- دالة عليا ترجع الإجابة + الاستشهادات ----------
def answer_question(question: str, top_k: int = TOP_K) -> Dict[str, Any]:
    chunks = retrieve_context(question, k=top_k)

    if not chunks:
        return {
            "answer": "لا توجد مراجع كافية للإجابة على سؤالك حاليًا.",
            "citations": [],
            "used_chunks": []
        }

    raw_answer = call_gemini(question, chunks)

    # أبسط شكل للاستشهادات: [1], [2], ... بناءً على ترتيب المقاطع
    citations = [f"[{i}]" for i in range(1, len(chunks) + 1)]

    return {
        "answer": raw_answer,
        "citations": citations,
        "used_chunks": [c.__dict__ for c in chunks]
    }