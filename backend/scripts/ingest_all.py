import os
import sys

# Ensure backend is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ingest_half_sync import ingest_pipeline as ingest_english
from scripts.ingest_marathi import ingest_pipeline as ingest_marathi

def run_all():
    print("="*60)
    print("STARTING FULL INGESTION PIPELINE (ENGLISH -> MARATHI)")
    print("="*60)
    
    try:
        print("\n\n[1/2] INGESTING ENGLISH DATASET...")
        ingest_english()
        
        print("\n\n[2/2] INGESTING MARATHI DATASET...")
        ingest_marathi()
        
        print("\n\n" + "="*60)
        print("[SUCCESS] ALL DATASETS INGESTED SUCCESSFULLY!")
        print("="*60)
    except Exception as e:
        print("\n[CRITICAL ERROR] Ingestion failed:", e)

if __name__ == "__main__":
    run_all()
