import uuid
from pathlib import Path

import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_URL  = "http://localhost:6333"
COLLECTION  = "hal_ai_docs"
EMBED_MODEL = "nomic-embed-text:latest"
VECTOR_SIZE = 768
CHUNK_WORDS = 150
OVERLAP     = 20


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def chunk(text: str) -> list[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + CHUNK_WORDS, len(words))
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_WORDS - OVERLAP
    return chunks


def ingest_file(client: QdrantClient, path: Path) -> int:
    chunks = chunk(path.read_text())
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embed(c),
            payload={"source": path.name, "chunk_index": i, "text": c},
        )
        for i, c in enumerate(chunks)
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def main():
    client = QdrantClient(url=QDRANT_URL)

    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION}")
    else:
        print(f"Collection already exists: {COLLECTION}")

    docs_dir = Path(__file__).parent / "sample_docs"
    total = 0
    for doc in sorted(docs_dir.glob("*.txt")):
        count = ingest_file(client, doc)
        print(f"  {doc.name}: {count} chunks ingested")
        total += count

    print(f"\nDone — {total} chunks total in collection '{COLLECTION}'")


if __name__ == "__main__":
    main()
