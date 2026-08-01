import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import settings

print("Recreating Qdrant collection...")
client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=60.0)

client.recreate_collection(
    collection_name=settings.COLLECTION_NAME,
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

print("Collection recreated successfully!")
