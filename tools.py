import os, psycopg2
from dotenv import load_dotenv
from retrive import retrieve

load_dotenv(override=True)
conn = psycopg2.connect(os.environ["DATABASE_URL"])

TOOLS = [
    {
        "type": "function", "function":{
            "name": "get_order_status",
            "description": "Get the status, customer and last update time of an order by by its numeric ID.",
            "parameters":{"type":"object",
                        "properties":{"order_id":{"type":"integer"}},
                        "required":["order_id"]}
        }
    },
    {
        "type": "function","function":{
            "name": "search_docs",
            "description":"Search the ingested research papers (Transformer, RAG) for information.",
            "parameters":{"type":"object",
                        "properties":{"query":{"type":"string"}},
                        "required":["query"]}
        }
    }
]

def get_order_status(order_id):
    cur = conn.cursor()
    cur.execute("SELECT status, customer, updated_at FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "order not found"}
    return { "status": row[0], "customer": row[1], "updated_at": str(row[2])}

def search_docs(query):
    return {"results":[
        {"source": c["source"], "page": c["page"], "content": c["content"]}
        for c in retrieve(query, k=3)
    ]}

def run_tool(name, args):
    if name == "get_order_status":
        return get_order_status(args["order_id"])
    if name == "search_docs":
        return search_docs(args["query"])
    return { "error": f"unknown tool {name}"}