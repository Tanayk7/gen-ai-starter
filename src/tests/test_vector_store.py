from src.utils.vector_store import GenericVectorStore  # Assuming you saved the class in this file
import uuid

def main():
    # Initialize vector store (Chroma / FAISS / Pinecone based on .env)
    store = GenericVectorStore()

    # Sample documents
    docs = [
        "The Eiffel Tower is in Paris.",
        "Python is a popular programming language.",
        "The Great Wall of China is visible from space.",
        "OpenAI developed ChatGPT.",
        "Mount Everest is the tallest mountain in the world."
    ]

    # Generate unique string IDs for testing
    ids = [str(uuid.uuid4()) for _ in docs]
    metadatas = [{"source": "test"} for _ in docs]

    # Insert documents
    print("Inserting documents...")
    store.insert_documents(texts=docs, ids=ids, metadatas=metadatas)

    # Run similarity search
    query = "What's the tallest peak on Earth?"
    print(f"\nRunning similarity search for: '{query}'")
    results = store.similarity_search(query, top_k=3)

    print("\nTop Results:")
    for res in results:
        print(res)

    # Optional: Retrieve a document by ID (for Chroma / Pinecone / FAISS)
    print("\nRetrieving one document by ID:")
    retrieved = store.retrieve([ids[0]])
    print(retrieved)

    # Optional: Delete document
    print("\nDeleting one document...")
    store.delete_documents([ids[0]])
    print("Deleted.")

if __name__ == "__main__":
    main()