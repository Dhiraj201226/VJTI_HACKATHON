import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from core.config import settings

# Initialize embedding model
model = SentenceTransformer('BAAI/bge-small-en-v1.5')

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

collection_name = "maha_gr_collection"
try:
    collection = client.get_collection(name=collection_name)
except Exception:
    collection = client.create_collection(name=collection_name)

def get_embedding(text: str):
    embeddings = model.encode(text)
    return embeddings.tolist()

def add_documents(documents: list, metadatas: list, ids: list):
    embeddings = [get_embedding(doc) for doc in documents]
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

def search_gr(query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results

# Mock data for demonstration purposes
def seed_mock_data():
    if collection.count() == 0:
        docs = [
            "Government Resolution regarding establishment of AI Labs in Engineering Colleges. Budget limit is 50 Lakhs per college. Dept: Higher Education. Date: 2023-05-10. GR: HE-2023/1",
            "Updated policy on AI Labs in Technical Institutions. Budget increased to 1 Crore per college. Requires 30% private partnership. Dept: Technical Education. Date: 2024-01-15. GR: TE-2024/2",
            "Guidelines for procurement of computers in government colleges. Must use GeM portal. Dept: Finance. Date: 2022-11-20. GR: FIN-2022/9"
        ]
        metadatas = [
            {"department": "Higher Education", "date": "2023-05-10", "gr_number": "HE-2023/1", "policy_area": "AI Labs"},
            {"department": "Technical Education", "date": "2024-01-15", "gr_number": "TE-2024/2", "policy_area": "AI Labs"},
            {"department": "Finance", "date": "2022-11-20", "gr_number": "FIN-2022/9", "policy_area": "Procurement"}
        ]
        ids = ["gr1", "gr2", "gr3"]
        add_documents(docs, metadatas, ids)

seed_mock_data()
