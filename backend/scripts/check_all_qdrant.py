from qdrant_client import QdrantClient

try:
    client = QdrantClient(host="127.0.0.1", port=6333)
    collections = client.get_collections().collections
    for c in collections:
        info = client.get_collection(c.name)
        print(f"Collection: {c.name} | Points: {info.points_count}")
except Exception as e:
    print(e)
