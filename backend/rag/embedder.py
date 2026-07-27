from sentence_transformers import SentenceTransformer
from config import settings

# Load model globally to avoid reloading it multiple times
model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

def get_embedding(text: str) -> list[float]:
    """Generates a single embedding for a given text."""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a batch of texts."""
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
