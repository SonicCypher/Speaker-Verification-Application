import psycopg2
import os
from dotenv import load_dotenv
import numpy as np
import torch

# Load .env file
load_dotenv()

# Load DB config
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
}


def create_table_if_not_exists():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS speaker_embeddings (
            username TEXT PRIMARY KEY,
            embedding BYTEA
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_embedding_to_postgres(username, embedding_tensor):
    create_table_if_not_exists()

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # check username in databse, if send value error
    cur.execute("SELECT username FROM speaker_embeddings WHERE username = %s", (username,))
    if cur.fetchone() is not None:
        raise ValueError(f"Username '{username}' already exists in the database. Please use a different username.")
    
    # Serialize embedding tensor
    embedding_bytes = embedding_tensor.cpu().numpy().tobytes()

    cur.execute("""
        INSERT INTO speaker_embeddings (username, embedding)
        VALUES (%s, %s)
    """, (username, psycopg2.Binary(embedding_bytes)))

    conn.commit()
    cur.close()
    conn.close()
    print(f"[DB] Saved embedding for user: {username}")


def load_embedding_from_postgres(username):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    # Check if the username exists in the database
    cur.execute("SELECT username FROM speaker_embeddings WHERE username = %s", (username,))
    if cur.fetchone() is None:
        raise ValueError(f"Username '{username}' does not exist in the database. Please register first.")
    
    cur.execute("SELECT embedding FROM speaker_embeddings WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is None:
        raise ValueError(f"No embedding found for user: {username}")

    embedding_bytes = result[0]

    # Correct way to decode float32 tensor from bytes
    embedding_tensor = torch.from_numpy(np.frombuffer(embedding_bytes, dtype=np.float32))

    return embedding_tensor

