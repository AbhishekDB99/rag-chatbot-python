from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
client = OpenAI()

SYSTEM ="""Answer using ONLY the context below.
If the answer isnt in the context, say "I dont have that information in the document provided.
Cite which source each fact comes from."""

def generate(question, chunks):
    context = "\n\n---\n\n".join(f"[{c['source']} p.{c['page']}]\n{c['content']}" for c in chunks)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content