#!/usr/bin/env python3
"""Drop and recreate the hal_ai_docs collection. All data is lost."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_URL  = "http://localhost:6333"
COLLECTION  = "hal_ai_docs"
VECTOR_SIZE = 768

client = QdrantClient(url=QDRANT_URL)

existing = {c.name for c in client.get_collections().collections}
if COLLECTION in existing:
    client.delete_collection(COLLECTION)
    print(f"Deleted:  {COLLECTION}")
else:
    print(f"Not found: {COLLECTION} (nothing to delete)")

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)
print(f"Created:  {COLLECTION}  (vector_size={VECTOR_SIZE}, distance=COSINE)")
