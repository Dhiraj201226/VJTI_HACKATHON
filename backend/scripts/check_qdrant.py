from qdrant_client import QdrantClient

try:
    client = QdrantClient(host="127.0.0.1", port=6333)
    info = client.get_collection("government_resolutions")
    print(f"Points Count: {info.points_count}")
except Exception as e:
    print(e)
