"""Ingest all documents in ingestions/ into Qdrant.

Routing by extension:
  .pdf  → pdf_ingest (section-based chunking, image extraction)
  .txt  → word-based chunking (simple, no images)

Run from project root:
    python src/rag/ingest.py
    python src/rag/ingest.py path/to/specific.pdf
"""
import sys
import uuid
from pathlib import Path

import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from pdf_ingest import ingest_pdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INGESTIONS   = PROJECT_ROOT / "ingestions"

QDRANT_URL   = "http://localhost:6333"
COLLECTION   = "hal_ai_docs"
EMBED_MODEL  = "nomic-embed-text:latest"
VECTOR_SIZE  = 768
CHUNK_WORDS  = 150
OVERLAP      = 20


def _embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def _chunk_words(text: str) -> list[str]:
    words, chunks, start = text.split(), [], 0
    while start < len(words):
        end = min(start + CHUNK_WORDS, len(words))
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_WORDS - OVERLAP
    return chunks


def ingest_txt(client: QdrantClient, path: Path) -> int:
    chunks = _chunk_words(path.read_text())
    points = [
        PointStruct(
            id      = str(uuid.uuid4()),
            vector  = _embed(c),
            payload = {
                "text":       c,
                "source":     path.name,
                "section":    "",
                "subsection": "",
                "page_start": 0,
                "page_end":   0,
                "figures":    [],
            },
        )
        for c in chunks
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def ensure_collection(client: QdrantClient) -> None:
    existing = {c.name for c in client.get_collections().collections}
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION}")


def main() -> None:
    client = QdrantClient(url=QDRANT_URL)
    ensure_collection(client)

    # Single file mode: python ingest.py path/to/file.pdf
    if len(sys.argv) == 2:
        targets = [Path(sys.argv[1])]
    else:
        targets = sorted(INGESTIONS.glob("*.*"))

    if not targets:
        print(f"No files found in {INGESTIONS}")
        return

    total = 0
    for path in targets:
        if path.suffix.lower() == ".pdf":
            count = ingest_pdf(client, COLLECTION, path)
        elif path.suffix.lower() == ".txt":
            print(f"[txt] {path.name}")
            count = ingest_txt(client, path)
            print(f"  {count} chunks upserted")
        else:
            print(f"[skip] {path.name}  (unsupported type)")
            continue
        total += count

    print(f"\nDone — {total} total chunks in '{COLLECTION}'")


if __name__ == "__main__":
    main()
