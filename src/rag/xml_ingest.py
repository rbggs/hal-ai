#!/usr/bin/env python3
"""XML ingestion: structured DocBook/FrameMaker XML → Qdrant.

Chunking: one chunk per Sect4 (the most granular titled unit).
Images:   mapped from XML <Graphic entityref> IDs to extracted PNGs by
          global positional ordering (XML graphic #N ↔ PDF image #N).
          A companion PDF with the same stem must already have had its images
          extracted to data/figures/ before this runs.
"""
from __future__ import annotations

import re
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from pdf_ingest import (
    Chunk, PROJECT_ROOT, _source_slug, _clean_for_embed, _embed, _MIN_CHUNK_CHARS,
    upsert_chunks,
)
from qdrant_client import QdrantClient

_IMG_ID = re.compile(r"(\d{7,8})")


# ── image mapping ─────────────────────────────────────────────────────────────

def _find_figures_dir(xml_path: Path) -> Path | None:
    """Find the extracted-images directory for a companion PDF."""
    # Same stem, look for figures dir with matching slug
    pdf_path = xml_path.with_suffix(".pdf")
    if pdf_path.exists():
        slug = _source_slug(pdf_path)
        exact = PROJECT_ROOT / "data" / "figures" / slug
        if exact.exists():
            return exact
        # Trailing-dash variant (legacy naming when filename had trailing space)
        with_dash = PROJECT_ROOT / "data" / "figures" / (slug + "-")
        if with_dash.exists():
            return with_dash

    # Scan data/figures/ for any dir whose name starts with a close stem match
    stem_norm = re.sub(r"[\s_-]+", "-", xml_path.stem.lower()).strip("-")
    figures_root = PROJECT_ROOT / "data" / "figures"
    for d in figures_root.iterdir():
        if d.is_dir() and (d.name.startswith(stem_norm[:12]) or stem_norm[:12] in d.name):
            return d
    return None


def _sorted_pngs(figures_dir: Path) -> list[Path]:
    """Return all extracted PNGs sorted by page number then image index."""
    return sorted(
        figures_dir.glob("*.png"),
        key=lambda p: (
            int(m.group(1)) if (m := re.search(r"page(\d+)", p.name)) else 0,
            int(m.group(1)) if (m := re.search(r"img(\d+)", p.name)) else 0,
        ),
    )


def build_image_map(xml_path: Path) -> dict[str, str]:
    """Map XML image IDs (e.g. '21360020') → project-relative PNG path.

    Strategy: iterate ALL <Graphic> elements in document order; iterate all
    extracted PNGs in page order.  Map by global position — XML graphic #N
    corresponds to extracted PNG #N.  The 35 graphics without an entityref
    (decoratives or placeholders) still consume a position slot, keeping the
    index aligned.
    """
    figures_dir = _find_figures_dir(xml_path)
    if not figures_dir:
        return {}

    pngs = _sorted_pngs(figures_dir)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    id_to_png: dict[str, str] = {}
    for idx, graphic in enumerate(root.iter("Graphic")):
        if idx >= len(pngs):
            break
        ref = graphic.attrib.get("entityref", "")
        m = _IMG_ID.search(ref)
        if m:
            image_id = m.group(1)
            if image_id not in id_to_png:          # keep first occurrence
                id_to_png[image_id] = str(pngs[idx].relative_to(PROJECT_ROOT))

    return id_to_png


# ── text extraction ───────────────────────────────────────────────────────────

def _clean_text(el: ET.Element) -> str:
    return " ".join(t.strip() for t in el.itertext() if t.strip())


def _sect4_images(sect4: ET.Element, image_map: dict[str, str]) -> list[str]:
    """Collect unique PNG paths for all <Graphic> references in this Sect4."""
    seen: set[str] = set()
    paths: list[str] = []
    for graphic in sect4.iter("Graphic"):
        ref = graphic.attrib.get("entityref", "")
        m = _IMG_ID.search(ref)
        if m:
            png = image_map.get(m.group(1))
            if png and png not in seen:
                seen.add(png)
                paths.append(png)
    return paths


# ── chunking ──────────────────────────────────────────────────────────────────

def extract_xml_chunks(xml_path: Path, image_map: dict[str, str]) -> list[Chunk]:
    """Parse XML into one Chunk per Sect4, with precise per-Sect4 image lists."""
    source = xml_path.name
    tree   = ET.parse(xml_path)
    root   = tree.getroot()
    chunks: list[Chunk] = []

    sect1       = root.find(".//Sect1")
    sect1_title = sect1.findtext("Title") or "" if sect1 is not None else ""

    for sect2 in (sect1.findall("Sect2") if sect1 is not None else []):
        sect2_title = sect2.findtext("Title") or ""

        for sect3 in sect2.findall("Sect3"):
            sect3_title = sect3.findtext("Title") or ""

            for sect4 in sect3.findall("Sect4"):
                sect4_title = sect4.findtext("Title") or ""
                text        = _clean_text(sect4)

                if len(text) < _MIN_CHUNK_CHARS:
                    continue

                chunks.append(Chunk(
                    text       = text,
                    source     = source,
                    section    = sect3_title,
                    subsection = f"{sect3_title} / {sect4_title}",
                    page_start = 0,
                    page_end   = 0,
                    figures    = _sect4_images(sect4, image_map),
                ))

    return chunks


# ── embedding override ────────────────────────────────────────────────────────

def _upsert_xml_chunks(client: QdrantClient, collection: str,
                       chunks: list[Chunk], doc_title: str) -> int:
    """Embed and upsert XML chunks with rich section-hierarchy prefix."""
    from qdrant_client.models import PointStruct
    points  = []
    skipped = 0
    for chunk in chunks:
        if len(chunk.text) < _MIN_CHUNK_CHARS:
            skipped += 1
            continue
        # Prefix: doc_title + section + subsection → dense semantic signal
        embed_text = f"{doc_title} {chunk.section} {chunk.subsection} {chunk.text}"
        points.append(PointStruct(
            id      = str(uuid.uuid4()),
            vector  = _embed(embed_text),
            payload = {
                "text":       chunk.text,
                "source":     chunk.source,
                "section":    chunk.section,
                "subsection": chunk.subsection,
                "page_start": chunk.page_start,
                "page_end":   chunk.page_end,
                "figures":    chunk.figures,
            },
        ))
    client.upsert(collection_name=collection, points=points)
    if skipped:
        print(f"  Skipped {skipped} stub chunks (< {_MIN_CHUNK_CHARS} chars)")
    return len(points)


# ── public entry point ────────────────────────────────────────────────────────

def ingest_xml(client: QdrantClient, collection: str, xml_path: Path) -> int:
    print(f"[xml] {xml_path.name}")
    image_map = build_image_map(xml_path)
    print(f"  Image map: {len(image_map)} IDs resolved")
    chunks    = extract_xml_chunks(xml_path, image_map)
    print(f"  {len(chunks)} chunks")
    count = _upsert_xml_chunks(client, collection, chunks, doc_title="EATs Service Manual")
    print(f"  {count} points upserted")
    return count
