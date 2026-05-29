#!/usr/bin/env python3
"""Show a beautified summary of the Qdrant server and hal_ai_docs collection."""
from collections import Counter

from qdrant_client import QdrantClient

QDRANT_URL = "http://localhost:6333"
COLLECTION = "hal_ai_docs"

SEP  = "=" * 60
SEP2 = "-" * 60


def section(title: str):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


def row(label: str, value):
    print(f"  {label:<30} {value}")


client = QdrantClient(url=QDRANT_URL)

# ── 1. Server info ─────────────────────────────────────────────
section("🖥️  QDRANT SERVER")
try:
    info = client.http.cluster_api.cluster_status().result
    row("Mode:", info.status)
except Exception:
    row("Mode:", "standalone (cluster API not available)")

# ── 2. All collections ─────────────────────────────────────────
section("📦  ALL COLLECTIONS")
collections = client.get_collections().collections
if not collections:
    print("  (no collections found)")
else:
    print(f"  {'NAME':<30} {'STATUS':<10} {'POINTS'}")
    print(f"  {SEP2}")
    for col in collections:
        info = client.get_collection(col.name)
        pts  = info.points_count
        sts  = info.status
        icon = "🟢" if str(sts) == "green" else "🟡"
        print(f"  {col.name:<30} {icon} {str(sts):<8} {pts} points")

# ── 3. Collection detail ───────────────────────────────────────
section(f"🔍  COLLECTION DETAIL: {COLLECTION}")
try:
    col = client.get_collection(COLLECTION)
    cfg = col.config.params
    vec = cfg.vectors

    status_icon = "🟢" if str(col.status) == "green" else "🟡"
    opt_icon    = "✅" if str(col.optimizer_status) == "ok" else "⚠️"

    row("Status:",           f"{status_icon}  {col.status}")
    row("Optimizer:",        f"{opt_icon}  {col.optimizer_status}")
    row("Total chunks:",     f"{col.points_count}")
    row("Indexed vectors:",  f"{col.indexed_vectors_count}")
    row("Segments:",         f"{col.segments_count}")
    row("Vector size:",      f"{vec.size} dimensions")
    row("Distance metric:",  f"{vec.distance}")
    row("On-disk payload:",  f"{cfg.on_disk_payload}")

    hnsw = col.config.hnsw_config
    print(f"\n  {'HNSW Config':}")
    print(f"  {SEP2}")
    row("  m (connections):", hnsw.m)
    row("  ef_construct:",    hnsw.ef_construct)
    row("  Full scan threshold:", hnsw.full_scan_threshold)

except Exception as e:
    print(f"  ❌  Could not fetch collection: {e}")

# ── 4. Chunks by source ────────────────────────────────────────
section("📄  CHUNKS BY SOURCE DOCUMENT")
try:
    all_points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=1000,
        with_payload=True,
        with_vectors=False,
    )
    sources = Counter(p.payload.get("source", "unknown") for p in all_points)
    total   = sum(sources.values())

    print(f"  {'SOURCE':<40} {'CHUNKS':>6}  {'%':>5}")
    print(f"  {SEP2}")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {src:<40} {count:>6}  {pct:>4.1f}%")
    print(f"  {SEP2}")
    print(f"  {'TOTAL':<40} {total:>6}")

except Exception as e:
    print(f"  ❌  Could not scroll points: {e}")

# ── 5. Sample chunks ───────────────────────────────────────────
section("🧩  SAMPLE CHUNKS (first 3)")
try:
    sample, _ = client.scroll(
        collection_name=COLLECTION,
        limit=3,
        with_payload=True,
        with_vectors=False,
    )
    for i, pt in enumerate(sample, 1):
        p = pt.payload
        print(f"\n  [{i}] ID: {pt.id}")
        print(f"      Source : {p.get('source', 'n/a')}")
        print(f"      Title  : {p.get('title', 'n/a')}")
        snippet = p.get("text", "")[:200].replace("\n", " ")
        print(f"      Text   : {snippet}...")

except Exception as e:
    print(f"  ❌  Could not fetch sample chunks: {e}")

print(f"\n{SEP}\n")
