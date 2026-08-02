import sqlite3
import os

DB_PATH = "data/gr_database.db"

db_file = DB_PATH
if not os.path.exists(db_file):
    db_file = "data/maha_gr.db"

print(f"Connecting to {db_file}")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("status", "VARCHAR DEFAULT 'PENDING_DS_REVIEW'"),
        ("sha256_hash", "VARCHAR"),
        ("desk_officer_notes", "VARCHAR"),
        ("deputy_secy_notes", "VARCHAR"),
        ("secy_notes", "VARCHAR"),
        ("draft_json", "VARCHAR"),
        ("current_hash", "VARCHAR"),
        ("desk_officer_hash", "VARCHAR"),
        ("deputy_secy_hash", "VARCHAR"),
        ("priority", "VARCHAR DEFAULT 'Standard'")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE generated_grs ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete!")
except Exception as e:
    print(f"Migration failed: {e}")
