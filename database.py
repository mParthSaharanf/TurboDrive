import sqlite3
import os

DB_FILE = "turbodrive_state.db"

def init_db():
    """Creates the state tracking table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                session_uri TEXT,
                chunk_index INTEGER,
                start_byte INTEGER,
                end_byte INTEGER,
                status TEXT DEFAULT 'PENDING',
                UNIQUE(file_path, chunk_index)
            )
        """)
        conn.commit()

def register_chunks(file_path, session_uri, chunk_tasks):
    """
    Saves all the chunks for a file into the database.
    chunk_tasks is a list of tuples: (chunk_index, start_byte, end_byte)
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for index, start, end in chunk_tasks:
            # INSERT OR IGNORE ensures that if we restart an interrupted upload,
            # we don't overwrite rows that might already be marked 'COMPLETED'
            cursor.execute("""
                INSERT OR IGNORE INTO upload_chunks (file_path, session_uri, chunk_index, start_byte, end_byte)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, session_uri, index, start, end))
        conn.commit()

def get_next_pending_chunk(file_path):
    """
    Finds a single chunk that is still 'PENDING' or 'FAILED' for a worker to pick up.
    It temporarily sets it to 'UPLOADING' so two workers don't grab the same chunk.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Find one pending chunk
        cursor.execute("""
            SELECT id, session_uri, chunk_index, start_byte, end_byte 
            FROM upload_chunks 
            WHERE file_path = ? AND (status = 'PENDING' OR status = 'FAILED')
            LIMIT 1
        """, (file_path,))
        row = cursor.fetchone()
        
        if row:
            chunk_id = row[0]
            # Lock it so another worker doesn't touch it
            cursor.execute("UPDATE upload_chunks SET status = 'UPLOADING' WHERE id = ?", (chunk_id,))
            conn.commit()
            return row  # Returns: (id, session_uri, chunk_index, start_byte, end_byte)
        return None

def update_chunk_status(chunk_id, status):
    """Updates a chunk's status to COMPLETED or FAILED based on network result."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE upload_chunks SET status = ? WHERE id = ?", (status, chunk_id))
        conn.commit()

# Always ensure the database table is ready when this module is imported
init_db()