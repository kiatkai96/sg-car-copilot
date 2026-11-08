"""STEP A of RAG: read your files, cut them into pieces, and save them in a search index.

Run with:   python -m src.ingest
Run it again any time you change something in the data folder.
"""
import csv

import chromadb

from .config import CARS_CSV, CHUNK_CHARS, COLLECTION, DB_DIR, DOCS_DIR
from .embed import embed

PLACEHOLDER = "PASTE OFFICIAL TEXT HERE"


def chunk_text(text, max_chars=CHUNK_CHARS):
    """Cut a long text into small pieces ("chunks").

    Why? The AI can only read a few pieces at a time, and small pieces make
    search more precise. We keep the last line of each chunk at the start of the
    next one so a sentence is never cut off from its context.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    chunks, current, size = [], [], 0
    for line in lines:
        if size + len(line) > max_chars and current:
            chunks.append("\n".join(current))
            current = current[-1:]  # small overlap
            size = sum(len(x) for x in current)
        current.append(line)
        size += len(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def load_doc_chunks():
    items = []
    for path in sorted(DOCS_DIR.glob("*")):
        if path.suffix.lower() not in (".md", ".txt"):
            continue
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER in text:
            print(f"  [skipped] {path.name} still has the placeholder - paste the real text in.")
            continue
        pieces = chunk_text(text)
        for p in pieces:
            # Putting the file name in the text helps search find the right topic.
            items.append({"text": f"Source: {path.name}\n{p}", "source": path.name})
        print(f"  [ok] {path.name}: {len(pieces)} chunks")
    return items


def load_car_rows():
    items = []
    if not CARS_CSV.exists():
        return items
    with open(CARS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            price = (row.get("approx_price_sgd") or "").strip()
            if not price:
                continue  # skip rows you haven't filled in yet
            # Build the description from whatever columns are filled in
            # (electric cars have no engine size, some rows have no seat count).
            cc = (row.get("engine_cc") or "").strip()
            seats = (row.get("seats") or "").strip()
            parts = [row.get("body_type", "").strip()]
            if cc:
                parts.append(f"{cc}cc")
            parts.append(row.get("fuel", "").strip())
            if seats:
                parts.append(f"{seats} seats")
            spec = ", ".join(p for p in parts if p)
            text = (
                f"Car model: {row['make']} {row['model']} ({spec}). "
                f"Approximate price with COE: S${price}. Notes: {row.get('notes', '')}"
            )
            items.append({"text": text, "source": "cars.csv"})
    print(f"  [ok] cars.csv: {len(items)} rows")
    return items


def main():
    print("Reading files...")
    items = load_doc_chunks() + load_car_rows()
    if not items:
        print("Nothing to index yet! Fill in data/docs/*.md first (see the guide).")
        return

    print(f"Turning {len(items)} chunks into numbers (first run downloads a small model)...")
    vectors = embed([i["text"] for i in items])

    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION)  # start fresh each time
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    # Add in batches so big datasets don't choke
    B = 500
    for start in range(0, len(items), B):
        batch = items[start:start + B]
        col.add(
            ids=[f"chunk-{start + i}" for i in range(len(batch))],
            documents=[b["text"] for b in batch],
            embeddings=vectors[start:start + B],
            metadatas=[{"source": b["source"]} for b in batch],
        )
    print(f"Done. Saved {len(items)} chunks to the search index.")


if __name__ == "__main__":
    main()
