import sys
import os
from pathlib import Path
import logging
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rag.embedder import get_embeddings_batch
from rag.chunker import chunk_grs
from rag.parser import parse_grs
import uuid

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to the New Server
QDRANT_HOST = "127.0.0.1"
QDRANT_PORT = 6333
COLLECTION_NAME = "government_resolutions"

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=120.0)

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

def ingest_pipeline():
    print("=" * 60)
    logger.info("Starting Half Sync ingestion pipeline...")

    # Set custom dataset path for this script
    os.environ["DATASET_PATH"] = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        "mahGRs", "GR_combine", "english_half_sync.txt"
    )

    BASE_DIR = Path(__file__).parent.parent
    progress_file = BASE_DIR / "data" / "ingest_half_sync_progress.txt"
    start_from_gr = 0

    if progress_file.exists():
        try:
            start_from_gr = int(progress_file.read_text().strip())
            print(f"Resuming ingestion from GR No. {start_from_gr}...")
        except ValueError:
            pass

    # Use the existing parser generator
    gr_generator = parse_grs(start_from_gr=start_from_gr)
    chunk_generator = chunk_grs(gr_generator)

    BATCH_SIZE = 64
    current_batch = []
    processed_grs = set()
    uploaded_chunks = 0
    skipped_batches = 0

    try:
        for chunk in chunk_generator:
            current_batch.append(chunk)
            processed_grs.add(chunk.gr_no)

            if len(processed_grs) % 1000 == 0:
                print(f"Processed GRs : {len(processed_grs)} | Uploaded Chunks : {uploaded_chunks}")

            if len(current_batch) >= BATCH_SIZE:
                try:
                    texts = [c.text for c in current_batch]
                    embeddings = get_embeddings_batch(texts)
                    
                    points = []
                    for c, embedding in zip(current_batch, embeddings):
                        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{c.gr_no}-{c.chunk_id}"))
                        payload = {
                            "gr_no": c.gr_no,
                            "department": c.department,
                            "source_file": c.source_file,
                            "language": c.language,
                            "chunk_id": c.chunk_id,
                            "text": c.text
                        }
                        points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
                        
                    client.upsert(collection_name=COLLECTION_NAME, points=points)

                    uploaded_chunks += len(current_batch)
                    max_gr_in_batch = max(c.gr_no for c in current_batch)
                    progress_file.parent.mkdir(parents=True, exist_ok=True)
                    progress_file.write_text(str(max_gr_in_batch))
                    
                    stats_file = BASE_DIR / "data" / "ingestion_stats.json"
                    import json
                    stats_file.write_text(json.dumps({"total_grs": len(processed_grs), "ai_skipped": 0}))

                    print(f"[OK] Ingested up to GR {max_gr_in_batch} | Total Chunks: {uploaded_chunks}")
                except Exception as e:
                    skipped_batches += 1
                    print(f"[ERROR] Error during batch: {e}")
                finally:
                    current_batch = []

        if current_batch:
            try:
                texts = [c.text for c in current_batch]
                embeddings = get_embeddings_batch(texts)
                points = []
                for c, embedding in zip(current_batch, embeddings):
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{c.gr_no}-{c.chunk_id}"))
                    payload = {
                        "gr_no": c.gr_no,
                        "department": c.department,
                        "source_file": c.source_file,
                        "language": c.language,
                        "chunk_id": c.chunk_id,
                        "text": c.text
                    }
                    points.append(PointStruct(id=point_id, vector=embedding, payload=payload))
                
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                uploaded_chunks += len(current_batch)
                max_gr_in_batch = max(c.gr_no for c in current_batch)
                progress_file.write_text(str(max_gr_in_batch))
                print(f"[OK] Ingested up to GR {max_gr_in_batch} | Total Chunks: {uploaded_chunks}")
            except Exception as e:
                print(f"Final batch failed: {e}")

        print("[DONE] INGESTION FINISHED")
    except Exception as e:
        print("[CRASH] INGESTION CRASHED")
        traceback.print_exc()

if __name__ == "__main__":
    ingest_pipeline()
