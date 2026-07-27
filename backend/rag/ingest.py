import logging
import traceback
import os
from pathlib import Path

from .parser import parse_grs
from .chunker import chunk_grs
from .embedder import get_embeddings_batch
from .qdrant_db import upload_chunks

logger = logging.getLogger(__name__)


def ingest_pipeline():
    """
    Parser -> Chunker -> Embeddings -> Qdrant
    """

    print("=" * 60)
    print("🚀 INGESTION STARTED")
    print("=" * 60)

    progress_file = Path("backend/data/ingest_progress.txt")
    start_from_gr = 0

    if progress_file.exists():
        try:
            start_from_gr = int(progress_file.read_text().strip())
            print(f"Resuming ingestion from GR No. {start_from_gr}...")
        except ValueError:
            pass

    logger.info(f"Starting ingestion pipeline from GR {start_from_gr}...")

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
                print(
                    f"Processed GRs : {len(processed_grs)} | Uploaded Chunks : {uploaded_chunks}"
                )

            if len(current_batch) >= BATCH_SIZE:

                try:

                    texts = [c.text for c in current_batch]

                    print(
                        f"Embedding batch of {len(texts)} chunks..."
                    )

                    embeddings = get_embeddings_batch(texts)

                    print("Uploading batch to Qdrant...")

                    upload_chunks(current_batch, embeddings)

                    uploaded_chunks += len(current_batch)
                    
                    max_gr_in_batch = max(c.gr_no for c in current_batch)
                    progress_file.parent.mkdir(parents=True, exist_ok=True)
                    progress_file.write_text(str(max_gr_in_batch))

                    uploaded_grs = sorted(list(set(c.gr_no for c in current_batch)))
                    for gr in uploaded_grs:
                        print(f"✓ Successfully ingested GR No. {gr}")
                    
                    print(f"  -> Total Chunks Uploaded so far: {uploaded_chunks}")

                except Exception as e:

                    skipped_batches += 1

                    print("\n" + "=" * 60)
                    print("❌ ERROR DURING BATCH")
                    print(e)
                    traceback.print_exc()
                    print("=" * 60 + "\n")

                finally:
                    current_batch = []

        if current_batch:

            try:

                texts = [c.text for c in current_batch]

                embeddings = get_embeddings_batch(texts)

                upload_chunks(current_batch, embeddings)

                uploaded_chunks += len(current_batch)
                
                max_gr_in_batch = max(c.gr_no for c in current_batch)
                progress_file.write_text(str(max_gr_in_batch))

                uploaded_grs = sorted(list(set(c.gr_no for c in current_batch)))
                for gr in uploaded_grs:
                    print(f"✓ Successfully ingested GR No. {gr}")
                    
                print(f"  -> Total Chunks Uploaded so far: {uploaded_chunks}")

            except Exception as e:

                print("\nFinal batch failed")
                print(e)
                traceback.print_exc()

        print("\n" + "=" * 60)
        print("✅ INGESTION FINISHED")
        print("=" * 60)
        print(f"Total GRs Processed : {len(processed_grs)}")
        print(f"Total Chunks Uploaded : {uploaded_chunks}")
        print(f"Skipped Batches : {skipped_batches}")
        print("=" * 60)

        logger.info(
            f"Finished. GRs={len(processed_grs)}, Uploaded={uploaded_chunks}"
        )

        return uploaded_chunks

    except Exception as e:

        print("\n" + "=" * 60)
        print("💥 INGESTION CRASHED")
        print(e)
        traceback.print_exc()
        print("=" * 60)

        raise