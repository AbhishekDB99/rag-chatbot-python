from retrive import retrieve
from generate import generate

def main():
    print("RAG Chatbot - type 'exit' to quit")
    while True:
        question = input("\nYou:")
        if question.lower() == "exit":
            break
        chunks = retrieve(question, k=5)
        chunks = [c for c in chunks if c["distance"] < 0.7 ]
        for c in chunks:
            print(f"{c['distance']:.3f}| {c['content'][:80]}")
        if not chunks:
            print("Bot: No relevant documents found.")
            continue
        print(f"\nBot: {generate(question, chunks)}")
        
if __name__ == "__main__":
    main()