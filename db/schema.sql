   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE TABLE IF NOT EXISTS chunks (
       id serial PRIMARY KEY,
       source text,
       content text,
       embedding vector(1536),
       page int
   );
   CREATE INDEX IF NOT EXISTS chunks_embedding_idx
       ON chunks USING hnsw (embedding vector_cosine_ops);