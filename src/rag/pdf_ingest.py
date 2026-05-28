"""PDF ingestion: section-based chunking + image extraction → Qdrant.

Heading detection uses pdfplumber font sizes:
  >= SECTION_FONT  → major section  (updates section label, starts new chunk)
  >= HEADING_FONT  → minor heading  (updates subsection label, starts new chunk)
  below            → body text      (accumulated into current chunk)

Images smaller than MIN_IMG_AREA pixels² are skipped (icons, decoratives).
All figure paths stored in Qdrant payloads are relative to project root.
"""
from __future__ import annotations

import io
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import ollama
import pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

PROJECT_ROOT  = Path(__file__).resolve().parent.parent.parent
EMBED_MODEL   = "nomic-embed-text:latest"
SECTION_FONT    = 14.0   # font size >= this → major section heading
HEADING_FONT    = 11.0   # font size >= this → minor heading / subsection
MIN_IMG_AREA    = 5000   # px² — below this = icon/decorative, skip
Y_TOLERANCE     = 3.0    # px — words within this y-band are on the same row
MAX_EMBED_CHARS = 7000   # nomic-embed-text context = 2048 tokens (~8192 chars); leave buffer


# ── data model ────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    text: str
    source: str
    section: str
    subsection: str
    page_start: int
    page_end: int
    figures: list[str] = field(default_factory=list)


# ── image extraction ──────────────────────────────────────────────────────────

def _source_slug(pdf_path: Path) -> str:
    return re.sub(r"[\s_]+", "-", pdf_path.stem).lower()


def extract_images(pdf_path: Path) -> dict[int, list[str]]:
    """Extract raster images from all pages, save to data/figures/{slug}/.

    Returns {page_number: [relative_path, ...]} for pages that have images.
    Page numbers are 1-based (matching pdfplumber convention).
    """
    slug      = _source_slug(pdf_path)
    out_dir   = PROJECT_ROOT / "data" / "figures" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    page_figures: dict[int, list[str]] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            paths: list[str] = []
            pw, ph = page.width, page.height
            for idx, img in enumerate(page.images, start=1):
                w, h = img["width"], img["height"]
                # Skip icons, banners, and decoratives
                if w * h < MIN_IMG_AREA or min(w, h) < 35:
                    continue
                try:
                    # Clamp to page bounds (some PDFs have slightly out-of-bounds coords)
                    x0  = max(0, img["x0"])
                    top = max(0, img["top"])
                    x1  = min(pw, img["x1"])
                    bot = min(ph, img["bottom"])
                    cropped  = page.crop((x0, top, x1, bot))
                    pil_img  = cropped.to_image(resolution=150).original
                    filename = f"page{page.page_number}_img{idx}.png"
                    abs_path = out_dir / filename
                    pil_img.save(abs_path, format="PNG", optimize=True)
                    paths.append(str(abs_path.relative_to(PROJECT_ROOT)))
                except Exception as exc:
                    print(f"  [warn] p{page.page_number} img{idx}: {exc}")
            if paths:
                page_figures[page.page_number] = paths

    total = sum(len(v) for v in page_figures.values())
    print(f"  Extracted {total} images → data/figures/{slug}/")
    return page_figures


# ── text extraction + chunking ────────────────────────────────────────────────

def _row_text(words: list[dict]) -> str:
    return " ".join(w["text"] for w in sorted(words, key=lambda w: w["x0"]))


def _max_font(words: list[dict]) -> float:
    return max((w.get("size", 0) for w in words), default=0)


_NOISE_PATTERN = re.compile(r"^[^a-zA-Z0-9]*$")   # no alphanumeric chars at all
_LIGATURES     = {"ffi", "fi", "ff", "ffl", "fl"}
_MIN_CHUNK_CHARS = 50   # chunks shorter than this are skipped at upsert time


def _is_valid_heading(text: str) -> bool:
    """Reject ligature artifacts, CID encoding noise, and pure-symbol rows."""
    stripped = text.strip()
    if not stripped:
        return False
    # CID font encoding artifacts — (cid:NNN)
    if re.search(r"\(cid:\d+\)", stripped):
        return False
    if _NOISE_PATTERN.match(stripped):
        return False
    words = stripped.split()
    # Reject if every word is a known ligature token
    if all(w.lower() in _LIGATURES for w in words):
        return False
    # Must have at least one word with 3+ real alphabetic characters (not ligatures)
    return any(
        len(re.sub(r"[^a-zA-Z]", "", w)) >= 3 and w.lower() not in _LIGATURES
        for w in words
    )


def _group_rows(words: list[dict]) -> list[list[dict]]:
    buckets: dict[float, list[dict]] = {}
    for w in words:
        key = round(w["top"] / Y_TOLERANCE) * Y_TOLERANCE
        buckets.setdefault(key, []).append(w)
    return [buckets[k] for k in sorted(buckets)]


def extract_chunks(pdf_path: Path, page_figures: dict[int, list[str]]) -> list[Chunk]:
    """Parse PDF into section-based chunks, attaching figure paths per page range."""
    source     = pdf_path.name
    chunks:    list[Chunk] = []
    section    = ""
    subsection = ""
    body_lines: list[str] = []
    page_start = 1
    page_end   = 1

    def flush(current_page: int) -> None:
        nonlocal body_lines, page_start
        text = " ".join(body_lines).strip()
        if not text:
            body_lines = []
            return

        figures: list[str] = []
        for pg in range(page_start, current_page + 1):
            figures.extend(page_figures.get(pg, []))

        chunks.append(Chunk(
            text       = text,
            source     = source,
            section    = section,
            subsection = subsection,
            page_start = page_start,
            page_end   = current_page,
            figures    = figures,
        ))
        body_lines = []
        page_start = current_page

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pg    = page.page_number
            words = page.extract_words(extra_attrs=["fontname", "size"])
            h     = page.height
            # Strip page header / footer bands
            words = [w for w in words if w["top"] > 45 and w["bottom"] < h - 30]

            for row in _group_rows(words):
                font  = _max_font(row)
                clean = _row_text(row).strip()

                if not clean:
                    continue

                if font >= SECTION_FONT and _is_valid_heading(clean):
                    flush(pg)
                    section    = clean
                    subsection = clean
                    page_start = pg
                    page_end   = pg

                elif font >= HEADING_FONT and _is_valid_heading(clean):
                    flush(pg)
                    subsection = clean
                    page_start = pg
                    page_end   = pg

                else:
                    body_lines.append(clean)
                    page_end = pg

        flush(page_end)

    return chunks


# ── embedding + upsert ────────────────────────────────────────────────────────

_REPEATED_PUNCT = re.compile(r"([^\w\s])\1{2,}")   # 3+ identical non-word chars


def _clean_for_embed(text: str) -> str:
    """Remove dot-leaders and repeated punctuation that inflate token count."""
    text = _REPEATED_PUNCT.sub(" ", text)
    return re.sub(r" {2,}", " ", text).strip()


def _embed(text: str) -> list[float]:
    clean = _clean_for_embed(text)[:MAX_EMBED_CHARS]
    return ollama.embeddings(model=EMBED_MODEL, prompt=clean)["embedding"]


def upsert_chunks(client: QdrantClient, collection: str, chunks: list[Chunk]) -> int:
    points = []
    skipped = 0
    for chunk in chunks:
        if len(chunk.text) < _MIN_CHUNK_CHARS:
            skipped += 1
            continue
        embed_text = f"{chunk.section} {chunk.subsection} {chunk.text}"
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

def ingest_pdf(client: QdrantClient, collection: str, pdf_path: Path) -> int:
    """Full pipeline: extract images → chunk text → embed → upsert. Returns chunk count."""
    print(f"[pdf] {pdf_path.name}")
    page_figures = extract_images(pdf_path)
    chunks       = extract_chunks(pdf_path, page_figures)
    print(f"  {len(chunks)} chunks")
    count = upsert_chunks(client, collection, chunks)
    print(f"  {count} points upserted")
    return count
