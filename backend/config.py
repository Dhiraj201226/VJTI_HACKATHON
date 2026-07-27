import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Settings
    PROJECT_NAME = "MAHA-GR ALIGN - RAG Engine"
    API_V1_STR = "/api/v1"
    
    # Dataset
    DATASET_PATH = os.getenv("DATASET_PATH", "../mahGRs/GR_combine/english_all.txt")
    
    # Qdrant Settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_MEMORY_ONLY = os.getenv("QDRANT_MEMORY_ONLY", "True").lower() == "true"
    QDRANT_LOCAL_PATH = os.getenv("QDRANT_LOCAL_PATH", "./data/qdrant")
    COLLECTION_NAME = "government_resolutions"
    
    # Embedding Model Settings
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    
    # Chunking Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 600))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

settings = Config()
