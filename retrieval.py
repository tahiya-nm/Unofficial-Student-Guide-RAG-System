# Milestone 4 — Embedding and Retrieval
#
# Summary of steps:
#   1. Load chunks from ingestion.py
#   2. Embed all chunks using all-MiniLM-L6-v2 (local, no API key)
#   3. Store embeddings + metadata in a persistent ChromaDB collection
#   4. Provide a retrieve() function: query string -> top-k chunks + sources
#
# Run this file once to build the vector store, then import retrieve() in Milestone 5.
# Re-running will skip re-embedding if the collection already exists.
#
# Time complexity:  O(k) for embedding k chunks; O(1) per query at retrieval
# Space complexity: O(k) for storing k embeddings in ChromaDB

import chromadb
from sentence_transformers import SentenceTransformer
from ingestion import load_and_chunk

# --- Config ---
CHROMA_PATH = "./chroma_db"        # persistent local vector store
COLLECTION_NAME = "rmp_reviews"
EMBED_MODEL = "all-MiniLM-L6-v2"  # local model, no API key needed
TOP_K = 5                          # number of chunks to retrieve per query


def get_collection():
    """
    Return the ChromaDB collection, creating the client each time.
    PersistentClient saves to disk so embeddings survive between runs.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # cosine similarity for short text
    )
    return collection


def embed_and_store():
    """
    Load all chunks, embed them, and store in ChromaDB with metadata.
    Skips embedding if the collection is already populated.
    """
    collection = get_collection()

    # Skip if already populated — avoids re-embedding on every run
    if collection.count() > 0:
        print(f"Collection already contains {collection.count()} chunks. Skipping embedding.")
        return collection

    print("Loading and chunking documents...")
    chunks = load_and_chunk()

    print(f"\nEmbedding {len(chunks)} chunks with {EMBED_MODEL}...")
    model = SentenceTransformer(EMBED_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    # Store in ChromaDB — each chunk gets its text, embedding, and metadata
    print("\nStoring in ChromaDB...")
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source":    chunk["source"],
                "professor": chunk["professor"],
                "course":    chunk["course"]
            }
            for chunk in chunks
        ],
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    print(f"Stored {collection.count()} chunks in '{COLLECTION_NAME}'.")
    return collection


def retrieve(query, k=TOP_K):
    """
    Embed a query string and return the top-k most similar chunks.
    Returns a list of dicts: {text, source, professor, course, distance}
    Distance is cosine distance (lower = more similar).
    """
    model = SentenceTransformer(EMBED_MODEL)
    query_embedding = model.encode([query])[0].tolist()

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    # Flatten ChromaDB's nested response into a clean list
    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text":      results["documents"][0][i],
            "source":    results["metadatas"][0][i]["source"],
            "professor": results["metadatas"][0][i]["professor"],
            "course":    results["metadatas"][0][i]["course"],
            "distance":  round(results["distances"][0][i], 4)
        })

    return retrieved


if __name__ == "__main__":
    # Step 1: build the vector store
    embed_and_store()

    # Step 2: test retrieval with 3 evaluation plan queries
    # Per milestone 4 checkpoint: top results should be visibly relevant
    # and distance scores should be below 0.5 for good matches
    test_queries = [
        "What do students say about Graham Evans's lectures in CS225?",
        "Is CS374 with Jeff Erickson considered a difficult course?",
        "What are student complaints about Michael Nowak's CS128?"
    ]

    print("\n--- Retrieval Test (3 Evaluation Queries) ---\n")
    for query in test_queries:
        print(f"Query: {query}")
        results = retrieve(query)
        for r in results:
            print(f"  [{r['distance']}] {r['professor']} | {r['course']} | {r['source']}")
            print(f"  {r['text'][r['text'].index(chr(10))+1:r['text'].index(chr(10))+150]}")
            print()
        print("-" * 60)