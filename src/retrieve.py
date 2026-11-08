"""STEP B of RAG: given a question, find the most relevant pieces of text."""
import chromadb

from .config import COLLECTION, DB_DIR, TOP_K
from .embed import embed


def search(question, k=TOP_K):
    """Returns the k best-matching chunks, best first.

    'distance' means how far apart in meaning: 0 = identical, bigger = less related.
    """
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_collection(COLLECTION)  # errors if you haven't run ingest yet
    res = col.query(query_embeddings=embed([question]), n_results=k)
    results = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        results.append({"text": doc, "source": meta["source"], "distance": dist})
    return results


if __name__ == "__main__":
    # Quick test:  python -m src.retrieve
    q = input("Ask something: ")
    for r in search(q):
        print(f"\n[{r['source']}] distance={r['distance']:.3f}\n{r['text']}")
