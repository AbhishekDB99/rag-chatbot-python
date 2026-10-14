import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, run_tool

load_dotenv(override=True)
client = OpenAI()

SYSTEM="""You are an assistant with access to tools.
Use get_order_status for order questions and search_docs for questions about the papers.
Cite source and page for anything from search_docs. If a tool returns an error, say so."""

def run_agent(question, max_iters=5):
    messages = [
        {
            "role": "system", "content": SYSTEM
        },
        {
            "role": "user", "content": question
        }
    ]
    for i in range(max_iters):
        response = client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, tools =TOOLS, messages = messages
        )
        msg = response.choices[0].message
        messages.append(msg)
        
        if not msg.tool_calls:
            return msg.content
        
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"[tool] {tc.function.name}({args})")
            result = run_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id,
                            "content":json.dumps(result)})
    return "Reached max iterations without a final answer."

if __name__ == "__main__":
    while True:
        q=input("\nYou: ")
        if q.lower() == "exit":
            break
        print(f"\nBot: {run_agent(q)}")