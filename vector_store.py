
import os
import json
import numpy as np
import psycopg
from psycopg.rows import dict_row


from pgvector.psycopg import register_vector



DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))  # اضبطه لموديلك

def _conninfo():
    return f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

def get_conn():
    """
    ترجع اتصال psycopg مع تسجيل نوع vector عبر pgvector.
    استعمل autocommit=True لتبسيط أمثلة الإنشاء.
    """
    conn = psycopg.connect(_conninfo(), autocommit=True)
    # register pgvector adapter so we can pass numpy arrays directly
    register_vector(conn)
    return conn

def init_db(create_index: bool = False):
    """
    تفعيل الامتداد وإنشاء جدول المستندات.
    ينفّذ CREATE EXTENSION IF NOT EXISTS vector;
    ينشئ جدول 'documents' إذا مش موجود.
    Optionally creates an index (hnsw by default here).
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding vector({EMBEDDING_DIM})
            );
            """)

            if create_index:
                cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw
                ON documents USING hnsw (embedding vector_cosine_ops);
                """)

def upsert_document(doc_id: str, content: str, embedding: np.ndarray, metadata: dict | None = None):
    """
    يدخل doc أو يحدثه (UPSERT). 
    تمرّر embedding كـ numpy array أو list؛ register_vector يسمح بإرسال numpy مباشرة.
    """
    if metadata is None:
        metadata = {}
    embedding = np.asarray(embedding, dtype=float)
    if embedding.ndim != 1 or embedding.shape[0] != EMBEDDING_DIM:
        raise ValueError(f"Embedding dimension mismatch: expected {EMBEDDING_DIM}, got {embedding.shape}")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO documents (id, content, metadata, embedding)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE 
              SET content = EXCLUDED.content,
                  metadata = EXCLUDED.metadata,
                  embedding = EXCLUDED.embedding;
            """, (doc_id, content, json.dumps(metadata), embedding))

def bulk_insert(docs: list[dict]):
    """
    تحميل دفعات كبيرة. docs = [{'id':..., 'content':..., 'embedding': np.array, 'metadata': {...}}, ...]
    أسرع طريقة: COPY (binary) أو executemany; هذا مثال بسيط باستخدام executemany.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            for d in docs:
                upsert_document(d['id'], d['content'], d['embedding'], d.get('metadata'))

def query_similar(query_embedding: np.ndarray, top_k: int = 5, metric: str = "cosine"):
    """
    ترجع أقرب المستندات للـ query_embedding.
    metric: "cosine" | "l2" | "ip"
    النتيجة: قائمة ديكتات فيها id, content, metadata, score
    """
    query_embedding = np.asarray(query_embedding, dtype=float)
    if query_embedding.shape[0] != EMBEDDING_DIM:
        raise ValueError(f"Embedding dimension mismatch: expected {EMBEDDING_DIM}, got {query_embedding.shape}")


    if metric == "cosine":
        op = "<=>"
        # smaller = better
    elif metric == "l2":
        op = "<->"
    elif metric == "ip":
        op = "<#>"
    else:
        raise ValueError("metric must be 'cosine' or 'l2' or 'ip'")

    sql = f"""
    SELECT id, content, metadata, embedding {op} %s AS score
    FROM documents
    ORDER BY embedding {op} %s
    LIMIT %s;
    """

    with get_conn() as conn:

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, (query_embedding, query_embedding, top_k))
            rows = cur.fetchall()
            # convert psycopg row objects to plain python
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "content": r["content"],
                    "metadata": r["metadata"],
                    "score": float(r["score"])
                })
            return results

if __name__ == "__main__":
    # init DB and table (مرة واحدة)
    init_db(create_index=False)  # أنشئ index بعد رفع كم بيانات لو هتستخدم ivfflat

    sample_embedding = np.random.rand(EMBEDDING_DIM).astype(float)  # استبدل بمخرجات موديلك
    upsert_document("doc1", "ده نص تجريبي عن موضوع X", sample_embedding, {"source":"policy.pdf", "chunk_index": 1})


    q_emb = np.random.rand(EMBEDDING_DIM).astype(float)
    print(query_similar(q_emb, top_k=3, metric="cosine"))