import re
import ollama
import chainlit as cl
from pathlib import Path
from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
QDRANT_URL   = "http://localhost:6333"
COLLECTION   = "hal_ai_docs"
EMBED_MODEL  = "nomic-embed-text:latest"
LLM_MODEL    = "gemma4:latest"
TOP_K        = 8   # raised from 4 — relevant chunks for broad questions sit at rank 5-8

SYSTEM_PROMPT = """You are a precise technical assistant for Volvo truck service manuals.

Answer ONLY using the text in the provided context chunks. Do not add any facts, steps, or values from your training knowledge — even if they seem correct.

Rules:
- Use the exact wording from the context when stating diagnostic findings (e.g. "overheated" not "dirty").
- Synthesize ALL relevant findings across every chunk — do not stop at the first match.
- When the exact phrase is not in the manual, bridge to related conditions found in the chunks (e.g. "engine overheating" → transmission overheating, coolant issues, fan/belt failures).
- Cite the section name for every finding.
- If you are tempted to add a step or value not found in the chunks, do not include it.
- Only say "The manual does not cover this topic" if zero chunks contain anything related."""

QUERY_EXPANSION_PROMPT = """Generate 2 alternative search queries for the following question about a Volvo truck service manual.
Output only the 2 queries, one per line, no numbering, no explanation.

Question: {question}
Alternative queries:"""

qdrant = QdrantClient(url=QDRANT_URL)


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def generate_query_variants(question: str) -> list[str]:
    """Use the LLM to generate 2 alternative phrasings of the question."""
    try:
        response = ollama.generate(
            model  = LLM_MODEL,
            prompt = QUERY_EXPANSION_PROMPT.format(question=question),
            stream = False,
            options = {"temperature": 0.3, "num_predict": 60},
        )
        lines = [l.strip() for l in response["response"].strip().splitlines() if l.strip()]
        return lines[:2]
    except Exception:
        return []


def retrieve_multi(question: str) -> list[dict]:
    """Retrieve chunks for the question + 2 LLM-generated variants, deduplicated."""
    queries   = [question] + generate_query_variants(question)
    seen_keys: set[str] = set()
    merged:    list[dict] = []

    for q in queries:
        hits = qdrant.query_points(
            collection_name = COLLECTION,
            query           = embed(q),
            limit           = TOP_K,
            with_payload    = True,
        ).points
        for hit in hits:
            # Dedup by section + page — same passage can match multiple query variants
            key = f"{hit.payload.get('section','')}|{hit.payload.get('page_start','')}"
            if key not in seen_keys:
                seen_keys.add(key)
                merged.append(hit.payload)

    # Cap total context at TOP_K * 2 to avoid prompt overflow
    return merged[: TOP_K * 2]


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c.get('source', '')} — {c.get('section', '')} / {c.get('subsection', '')}  p{c.get('page_start','')}]\n{c['text']}"
        for c in chunks
    )
    return f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"


def collect_figures(chunks: list[dict]) -> list[str]:
    seen, paths = set(), []
    for chunk in chunks:
        for fig in chunk.get("figures", []):
            if fig not in seen:
                seen.add(fig)
                paths.append(fig)
    return paths


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])


@cl.on_message
async def on_message(message: cl.Message):
    question = message.content

    # Retrieve with query expansion
    chunks = await cl.make_async(retrieve_multi)(question)

    # Source citation text elements
    source_elements = [
        cl.Text(
            name    = f"{c.get('source','')} p{c.get('page_start','')}–{c.get('page_end','')}",
            content = f"**{c.get('section','')} / {c.get('subsection','')}**\n\n{c['text']}",
            display = "side",
        )
        for c in chunks
    ]

    # Inline image elements — deduplicated across all retrieved chunks
    image_elements = []
    for fig_path in collect_figures(chunks):
        abs_path = PROJECT_ROOT / fig_path
        if abs_path.exists():
            image_elements.append(
                cl.Image(
                    path    = str(abs_path),
                    name    = abs_path.name,
                    display = "inline",
                )
            )

    response = cl.Message(content="", elements=source_elements + image_elements)
    await response.send()

    prompt = build_prompt(question, chunks)
    stream = await cl.make_async(ollama.generate)(
        model  = LLM_MODEL,
        prompt = prompt,
        stream = True,
    )
    for chunk in stream:
        await response.stream_token(chunk["response"])

    await response.update()
