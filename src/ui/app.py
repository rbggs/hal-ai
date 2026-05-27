import ollama
import chainlit as cl
from qdrant_client import QdrantClient

QDRANT_URL  = "http://localhost:6333"
COLLECTION  = "hal_ai_docs"
EMBED_MODEL = "nomic-embed-text:latest"
LLM_MODEL   = "gemma4:latest"
TOP_K       = 3

SYSTEM_PROMPT = """You are a helpful assistant. Answer the question using only the provided context.
If the answer is not in the context, say "I don't have that information in the provided documents." """

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
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )
    return f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])


@cl.on_message
async def on_message(message: cl.Message):
    question = message.content

    # Retrieve relevant chunks
    chunks = retrieve(question)

    # Build source citation elements
    sources = [
        cl.Text(
            name=f"{c['source']} (chunk {c['chunk_index']})",
            content=c["text"],
            display="side",
        )
        for c in chunks
    ]

    # Stream answer from gemma4
    prompt   = build_prompt(question, chunks)
    response = cl.Message(content="", elements=sources)
    await response.send()

    stream = await cl.make_async(ollama.generate)(
        model=LLM_MODEL,
        prompt=prompt,
        stream=True,
    )
    for chunk in stream:
        await response.stream_token(chunk["response"])

    await response.update()
