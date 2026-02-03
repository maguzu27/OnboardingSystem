import sqlite3
from datetime import datetime

def setup_database():
    # Ensure this filename matches the one in your DatabaseManager
    db_name = "onboarding.db" 
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"Connected to {db_name}")

        # --- CREATE JOBS TABLE ---
        jobs_query = """
        CREATE TABLE IF NOT EXISTS Requirements_Setup_Items (
            Req_id INTEGER,
            Req_line_id INTEGER,
            Req_Name TEXT,
            Req_code TEXT,
            Req_Item_Type TEXT,
            Req_Description TEXT,
            PRIMARY KEY (Req_id, Req_line_id),
            FOREIGN KEY (Req_id) REFERENCES Requirements_Setup(Req_id) ON DELETE CASCADE
        )
        """
        cursor.execute(jobs_query)
        print("Table created.")

        conn.commit()
        print("Database schema initialized successfully.")

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()