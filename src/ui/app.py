import ollama
import chainlit as cl
from pathlib import Path
from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
QDRANT_URL   = "http://localhost:6333"
COLLECTION   = "hal_ai_docs"
EMBED_MODEL  = "nomic-embed-text:latest"
LLM_MODEL    = "gemma4:latest"
TOP_K        = 4

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question using only the provided context. "
    "If the answer is not in the context, say \"I don't have that information in the provided documents.\""
)

qdrant = QdrantClient(url=QDRANT_URL)


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def retrieve(question: str) -> list[dict]:
    hits = qdrant.query_points(
        collection_name=COLLECTION,
        query=embed(question),
        limit=TOP_K,
        with_payload=True,
    ).points
    return [h.payload for h in hits]


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{c.get('source', '')} — {c.get('section', '')} / {c.get('subsection', '')}]\n{c['text']}"
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
    chunks   = retrieve(question)

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
