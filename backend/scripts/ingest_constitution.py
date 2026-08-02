import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rag.embedder import get_embeddings_batch
import uuid

# Connect to the New Server
QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
COLLECTION_NAME = "constitution"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=60)

# Ensure Collection exists
try:
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
except Exception:
    exists = False

if not exists:
    print(f"Creating collection {COLLECTION_NAME}...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

def ingest_constitution():
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "constitution.json")
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    import json
    with open(filepath, "r", encoding="utf-8") as f:
        items = json.load(f)

    for idx, item in enumerate(items):
        item_text = f"{item['type']} {item['number']} - {item['title']}: {item['body']}"
        print(f"Embedding: {item_text[:40]}...")
        embeddings = get_embeddings_batch([item_text])
        
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"constitution-{idx}"))
        
        payload = {
            "source": "Constitution of India",
            "type": item["type"],
            "number": item["number"],
            "title": item["title"],
            "text": item_text
        }
        
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(id=point_id, vector=embeddings[0], payload=payload)
            ]
        )
    print("Constitution Ingestion Complete!")

if __name__ == "__main__":
    ingest_constitution()
