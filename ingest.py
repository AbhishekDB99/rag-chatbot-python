import sys, os
# import fitz
import pymupdf
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(override=True)
client = OpenAI()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
register_vector(conn)

def read_pdf(path):
    text = "\n".join(page.get_text() for page in pymupdf.open(path))
    return text.replace("\x00", "")

def chunk_text(text, size=200, overlap=30):
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i+size]) for i in range(0, len(words), step)]

def embed(text):
    res = client.embeddings.create(model="text-embedding-3-small", input=[text])
    return np.array(res.data[0].embedding)

def ingest(pdf_path):
    full_text = read_pdf(pdf_path)
    if not full_text.strip():
        print(f"No text extracted from {pdf_path}, skipping (scanned/image PDF?)")
        return
    chunks = chunk_text(full_text)
    cur = conn.cursor()
    for c in chunks:
        cur.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
            (os.path.basename(pdf_path), c, embed(c))
        )
    conn.commit()
    print(f"Ingested {len(chunks)} chunks from {pdf_path}")
    
if __name__ == "__main__":
    folder = sys.argv[1]
    for path in Path(folder).glob("*.pdf"):
        ingest(str(path))