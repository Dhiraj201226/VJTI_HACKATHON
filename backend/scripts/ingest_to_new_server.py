import sys
import os

# Add parent dir to path so we can import from rag
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rag.embedder import get_embeddings_batch
import uuid

# Connect to the New Server
QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
COLLECTION_NAME = "new_government_resolutions"

print(f"Connecting to Qdrant Server at {QDRANT_HOST}:{QDRANT_PORT}...")
try:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Make sure you run 'docker-compose up -d' first!")
    sys.exit(1)

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

def ingest_new_text(text: str, gr_no: int, department: str):
    print(f"Embedding text for GR {gr_no}...")
    embeddings = get_embeddings_batch([text])
    
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{gr_no}-1"))
    
    payload = {
        "gr_no": gr_no,
        "department": department,
        "source_file": "Custom_Ingestion",
        "language": "en",
        "chunk_id": 1,
        "text": text
    }
    
    print(f"Uploading to server collection '{COLLECTION_NAME}'...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(id=point_id, vector=embeddings[0], payload=payload)
        ]
    )
    print("Done!")

if __name__ == "__main__":
    # Example Usage:
    sample_text = "This is a new government resolution about infrastructure development in Pune."
    ingest_new_text(sample_text, gr_no=999999, department="Infrastructure")
