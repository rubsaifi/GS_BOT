"""
vector_store.py
Manages ChromaDB vector store with sentence-transformers embeddings (fully local/free).
"""

import chromadb
from chromadb.utils import embedding_functions
import os
import hashlib


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "goal_sheet_rag"


def get_embedding_function():
    """Use sentence-transformers all-MiniLM-L6-v2 — free, local, fast."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def build_vector_store(chunks: list[dict], force_rebuild: bool = False) -> chromadb.Collection:
    """
    Build or load ChromaDB collection from knowledge chunks.
    chunks: list of {"text": str, "metadata": dict}
    """
    client = get_chroma_client()
    ef = get_embedding_function()

    # Check if collection already exists and has data
    existing = client.list_collections()
    existing_names = [c.name for c in existing]

    if COLLECTION_NAME in existing_names and not force_rebuild:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ef
        )
        if collection.count() > 0:
            return collection
        # Empty collection — rebuild
        client.delete_collection(COLLECTION_NAME)

    elif COLLECTION_NAME in existing_names and force_rebuild:
        client.delete_collection(COLLECTION_NAME)

    # Create fresh collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # Add chunks
    documents, metadatas, ids = [], [], []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        meta = chunk.get("metadata", {})
        # Create stable ID from content hash
        doc_id = hashlib.md5(text.encode()).hexdigest()[:16] + f"_{i}"
        documents.append(text)
        metadatas.append(meta)
        ids.append(doc_id)

    # Batch insert (ChromaDB recommends batches of ≤ 5000)
    batch_size = 100
    for start in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[start:start+batch_size],
            metadatas=metadatas[start:start+batch_size],
            ids=ids[start:start+batch_size],
        )

    return collection


def retrieve_context(collection: chromadb.Collection, query: str, n_results: int = 5) -> str:
    """
    Retrieve top-k relevant chunks for a query.
    Returns a single string with all relevant context merged.
    """
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not docs:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for doc, dist in zip(docs, distances):
        relevance = 1 - dist  # cosine similarity
        if relevance > 0.1:   # filter out very low-relevance chunks
            context_parts.append(doc)

    return "\n\n---\n\n".join(context_parts) if context_parts else docs[0]
