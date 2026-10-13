import sys, os
# import fitz
import pymupdf
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv(override=True)
client = OpenAI()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
register_vector(conn)

def read_pdf(path):
    return [(i + 1, page.get_text().replace("\x00", ""))
            for i, page in enumerate(pymupdf.open(path))]

def chunk_text(text, size=200, overlap=30):
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i+size]) for i in range(0, len(words), step)]

def embed(text):
    res = client.embeddings.create(model="text-embedding-3-small", input=[text])
    return np.array(res.data[0].embedding)

def embed_many(texts, batch_size=100):
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        res = client.embeddings.create(model="text-embedding-3-small", input=batch)
        vectors.extend(np.array(d.embedding) for d in res.data)
    return vectors

def ingest(pdf_path):
    pages = read_pdf(pdf_path)
    rows = [(page_num, c) for page_num, text in pages for c in chunk_text(text)]
    if not rows:
        print(f"No text extracted from {pdf_path}, skipping (scanned/image PDF?)")
        return
    vectors = embed_many([c for _, c in rows])               # few API calls instead of ~100
    cur = conn.cursor()
    for (page_num, c), vec in zip(rows, vectors):
        cur.execute(
            "INSERT INTO chunks (source, page, content, embedding) VALUES (%s, %s, %s, %s)",
            (os.path.basename(pdf_path), page_num, c, vec)
        )
    conn.commit()
    print(f"Ingested {len(rows)} chunks from {pdf_path}")


if __name__ == "__main__":
    start = time.time()
    folder = sys.argv[1]
    for path in Path(folder).glob("*.pdf"):
        ingest(str(path))
    print(f"Took {time.time() - start:.1f}s")