import concurrent.futures
from sentence_transformers import SentenceTransformer
from config import settings

# Load model globally to avoid reloading it multiple times
model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

def get_embedding(text: str) -> list[float]:
    """Generates a single embedding for a given text."""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a batch of texts using ThreadPool for speed."""
    # SentenceTransformer releases the GIL during inference, so threads are perfectly fine
    def _encode_chunk(chunk):
        return model.encode(chunk, normalize_embeddings=True).tolist()
    
    # Split texts into smaller chunks for threads
    num_threads = 4
    chunk_size = max(1, len(texts) // num_threads)
    chunks = [texts[i:i + chunk_size] for i in range(0, len(texts), chunk_size)]
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for res in executor.map(_encode_chunk, chunks):
            results.extend(res)
            
    return results
