import logging
from .parser import parse_grs
from .chunker import chunk_grs
from .embedder import get_embeddings_batch
from .qdrant_db import upload_chunks

logger = logging.getLogger(__name__)

def ingest_pipeline():
    """
    Runs the full ingestion pipeline:
    Parser -> Chunker -> Embedding -> Qdrant
    """
    logger.info("Starting ingestion pipeline...")
    
    gr_generator = parse_grs()
    chunk_generator = chunk_grs(gr_generator)
    
    batch_size = 64
    current_batch = []
    
    grs_processed = set()
    total_grs_processed = 0
    
    for chunk in chunk_generator:
        current_batch.append(chunk)
        grs_processed.add(chunk.gr_no)
        
        # Report progress per 1000 GRs
        if len(grs_processed) % 1000 == 0 and len(grs_processed) > total_grs_processed:
            print(f"Processed {len(grs_processed)} GRs")
            logger.info(f"Processed {len(grs_processed)} GRs")
            total_grs_processed = len(grs_processed)
            
        if len(current_batch) >= batch_size:
            # Process batch
            texts = [c.text for c in current_batch]
            embeddings = get_embeddings_batch(texts)
            upload_chunks(current_batch, embeddings)
            current_batch = []
            
    # Process any remaining chunks in the final batch
    if current_batch:
        texts = [c.text for c in current_batch]
        embeddings = get_embeddings_batch(texts)
        upload_chunks(current_batch, embeddings)
        
    final_count = len(grs_processed)
    print(f"Ingestion completed. Total GRs processed: {final_count}")
    logger.info(f"Ingestion completed. Total GRs processed: {final_count}")
    return final_count
