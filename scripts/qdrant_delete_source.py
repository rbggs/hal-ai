#!/usr/bin/env python3
"""Delete all Qdrant points whose payload.source matches the given filename.

Usage:
    python scripts/qdrant_delete_source.py "volvo-trucks-basic-service-manual.pdf"
"""
import sys

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

QDRANT_URL = "http://localhost:6333"
COLLECTION = "hal_ai_docs"

if len(sys.argv) != 2:
    print("Usage: qdrant_delete_source.py <source-filename>")
    sys.exit(1)

source = sys.argv[1]
client = QdrantClient(url=QDRANT_URL)

existing = {c.name for c in client.get_collections().collections}
if COLLECTION not in existing:
    print(f"Collection '{COLLECTION}' does not exist — nothing to delete.")
    sys.exit(0)

before = client.count(collection_name=COLLECTION).count

client.delete(
    collection_name=COLLECTION,
    points_selector=Filter(
        must=[FieldCondition(key="source", match=MatchValue(value=source))]
    ),
)

after = client.count(collection_name=COLLECTION).count
print(f"Deleted {before - after} chunks  (source='{source}')")
print(f"Collection now has {after} chunks total.")
