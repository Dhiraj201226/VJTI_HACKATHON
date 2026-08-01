import logging
import traceback
import os
from pathlib import Path

from .parser import parse_grs
from .chunker import chunk_grs
from .embedder import get_embeddings_batch
from .qdrant_db import upload_chunks

logger = logging.getLogger(__name__)


import json

def ingest_pipeline():
    """
    Parser -> Chunker -> Embeddings -> Qdrant
    """
    print("=" * 60)
    logger.info("Starting ingestion pipeline...")

    BASE_DIR = Path(__file__).parent.parent
    DATASET_DIR = BASE_DIR.parent / "mahGRs" / "GR_combine"
    STATS_FILE = BASE_DIR / "data" / "ingestion_stats.json"
    
    datasets = [
        "half_sync.txt",
        "marathi_half_sync.txt"
    ]
    
    BATCH_SIZE = 64
    total_uploaded_chunks = 0
    total_skipped_batches = 0
    total_ai_skipped_grs = 0
    grand_total_grs = 0

    # Initialize stats file if it doesn't exist
    if not STATS_FILE.exists():
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATS_FILE.write_text(json.dumps({"total_grs": 0, "ai_skipped": 0}))
    else:
        try:
            stats = json.loads(STATS_FILE.read_text())
            grand_total_grs = stats.get("total_grs", 0)
            total_ai_skipped_grs = stats.get("ai_skipped", 0)
        except Exception:
            pass

    for dataset in datasets:
        filepath = DATASET_DIR / dataset
        progress_file = BASE_DIR / "data" / f"ingest_{dataset.split('.')[0]}_progress.txt"
        
        start_from_gr = 0
        if progress_file.exists():
            try:
                start_from_gr = int(progress_file.read_text().strip())
                print(f"Resuming {dataset} from GR No. {start_from_gr}...")
            except ValueError:
                pass

        logger.info(f"Processing {dataset} from GR {start_from_gr}...")
        print(f"\n{'='*60}\nSTARTING DATASET: {dataset}\n{'='*60}")

        if not filepath.exists():
            print(f"Warning: {filepath} not found! Skipping...")
            continue

        gr_generator = parse_grs(filepath=str(filepath), start_from_gr=start_from_gr)
        chunk_generator = chunk_grs(gr_generator)

        current_batch = []
        processed_grs = set()
        ai_skipped_grs = 0
        uploaded_chunks = 0
        skipped_batches = 0

        try:
            for chunk in chunk_generator:
                if chunk.department == "SKIPPED_BY_AI":
                    ai_skipped_grs += 1
                    continue
                
                current_batch.append(chunk)
                
                # Check if this is a newly seen GR to increment our global count
                if chunk.gr_no not in processed_grs:
                    processed_grs.add(chunk.gr_no)
                    grand_total_grs += 1

                if len(processed_grs) % 1000 == 0:
                    print(f"[{dataset}] Processed: {len(processed_grs)} | Skipped by AI: {ai_skipped_grs} | Uploaded: {uploaded_chunks}")

                if len(current_batch) >= BATCH_SIZE:
                    try:
                        texts = [c.text for c in current_batch]
                        embeddings = get_embeddings_batch(texts)
                        upload_chunks(current_batch, embeddings)

                        uploaded_chunks += len(current_batch)
                        
                        max_gr_in_batch = max(c.gr_no for c in current_batch)
                        progress_file.parent.mkdir(parents=True, exist_ok=True)
                        progress_file.write_text(str(max_gr_in_batch))
                        
                        # Update stats file for UI to read
                        STATS_FILE.write_text(json.dumps({
                            "total_grs": grand_total_grs, 
                            "ai_skipped": total_ai_skipped_grs + ai_skipped_grs
                        }))

                        print(f"[{dataset}] SUCCESS: Ingested batch (up to GR {max_gr_in_batch}) -> Total Chunks: {uploaded_chunks}")
                    except Exception as e:
                        skipped_batches += 1
                        print(f"\n[{dataset}] ERROR DURING BATCH")
                        traceback.print_exc()
                    finally:
                        current_batch = []

            # Final batch
            if current_batch:
                try:
                    texts = [c.text for c in current_batch]
                    embeddings = get_embeddings_batch(texts)
                    upload_chunks(current_batch, embeddings)

                    uploaded_chunks += len(current_batch)
                    
                    max_gr_in_batch = max(c.gr_no for c in current_batch)
                    progress_file.parent.mkdir(parents=True, exist_ok=True)
                    progress_file.write_text(str(max_gr_in_batch))
                    
                    STATS_FILE.write_text(json.dumps({
                        "total_grs": grand_total_grs, 
                        "ai_skipped": total_ai_skipped_grs + ai_skipped_grs
                    }))

                    print(f"[{dataset}] SUCCESS: Ingested final batch (up to GR {max_gr_in_batch}) -> Total Chunks: {uploaded_chunks}")
                except Exception as e:
                    print(f"\n[{dataset}] Final batch failed")
                    traceback.print_exc()

            print(f"\n{'='*60}\nFINISHED DATASET: {dataset}\n{'='*60}")
            print(f"Total GRs Processed : {len(processed_grs)}")
            print(f"Total GRs Skipped by AI : {ai_skipped_grs}")
            print(f"Total Chunks Uploaded : {uploaded_chunks}")
            print(f"Skipped Batches : {skipped_batches}")
            
            total_uploaded_chunks += uploaded_chunks
            total_skipped_batches += skipped_batches
            total_ai_skipped_grs += ai_skipped_grs
            
        except Exception as e:
            print(f"\n{'='*60}\n[{dataset}] INGESTION CRASHED")
            traceback.print_exc()
            print("=" * 60)
            raise

    print("\n" + "=" * 60)
    print("ALL DATASETS COMPLETELY INGESTED")
    print(f"Grand Total Chunks: {total_uploaded_chunks}")
    print(f"Grand Total Unique GRs: {grand_total_grs}")
    print(f"Grand Total Skipped by AI: {total_ai_skipped_grs}")
    print("=" * 60)
    
    return total_uploaded_chunks