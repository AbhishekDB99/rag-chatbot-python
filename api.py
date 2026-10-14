from fastapi import FastAPI
from pydantic import BaseModel
from retrive import retrieve
from generate import generate

app = FastAPI(title="RAG Chatbot")

class ChatRequest(BaseModel):
    question:str
    k: int=5
    
@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    chunks = [c for c in retrieve(req.question, k=req.k) if c["distance"] < 0.7]
    if not chunks:
        return {"answer": "No relevant documents found.", "sources":[]}
    answer = generate(req.question, chunks)
    sources = [
        {"source": c["source"], "page": c["page"], "distance": round(c["distance"], 3)}
        for c in chunks
    ]
    return {"answer":answer, "sources":sources}