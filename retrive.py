import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from ingest import embed

load_dotenv(override=True)
conn = psycopg2.connect(os.environ["DATABASE_URL"])
register_vector(conn)

def retrieve(question, k=5):
    vec = embed(question)
    cur = conn.cursor()
    cur.execute(
        "SELECT content, source, page, embedding <=> %s AS distance "
        "FROM chunks ORDER BY distance LIMIT %s",
        (vec, k)
    )
    return [{"content": r[0], "source": r[1], "page": r[2], "distance": r[3]} for r in cur.fetchall()]