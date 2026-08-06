import uuid
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import settings
from .models import GRChunk

# Initialize Qdrant Client
if settings.QDRANT_MEMORY_ONLY:
    client = QdrantClient(":memory:")
else:
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60.0)

def init_collection():
    """Ensures the collection exists."""
    try:
        collections = client.get_collections().collections
        exists = any(c.name == settings.COLLECTION_NAME for c in collections)
    except Exception:
        exists = False
    
    if not exists:
        # BAAI/bge-m3 outputs embeddings of size 1024
        client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

# Ensure collection is created upon module import
init_collection()

info = client.get_collection(settings.COLLECTION_NAME)
print("=" * 50)
print("Collection:", settings.COLLECTION_NAME)
print("Points Count:", info.points_count)
print("=" * 50)

def upload_chunks(chunks: list[GRChunk], embeddings: list[list[float]]):
    """Uploads a batch of chunks to Qdrant."""
    points = []
    
    for chunk, embedding in zip(chunks, embeddings):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.gr_no}-{chunk.chunk_id}"))
        
        payload = {
            "gr_no": chunk.gr_no,
            "department": chunk.department,
            "source_file": chunk.source_file,
            "language": chunk.language,
            "chunk_id": chunk.chunk_id,
            "text": chunk.text
        }
        
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        )
        
    if points:
        client.upsert(
            collection_name=settings.COLLECTION_NAME,
            points=points
        )

def search_qdrant(query_embedding: list[float], top_k: int = 10, query_filter=None):
    search_result = client.query_points(
        collection_name=settings.COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        query_filter=query_filter
    )
    return search_result.points
