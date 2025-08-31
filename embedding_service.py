from sentence_transformers import SentenceTransformer

# تحميل الموديل من HuggingFace
model = SentenceTransformer("BAAI/bge-small-en")  

def get_embeddings(texts):
    """
    ترجع الـ embeddings لقائمة من النصوص
    """
    embeddings = model.encode(texts, convert_to_tensor=True)
    return embeddings
