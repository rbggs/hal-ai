#!/usr/bin/env python3
import sys

import ollama
from qdrant_client import QdrantClient

QDRANT_URL  = "http://localhost:6333"
COLLECTION  = "hal_ai_docs"
EMBED_MODEL = "nomic-embed-text:latest"
LLM_MODEL   = "gemma4:latest"
TOP_K       = 3


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def retrieve(client: QdrantClient, question: str) -> list[dict]:
    hits = client.query_points(
        collection_name=COLLECTION,
        query=embed(question),
        limit=TOP_K,
        with_payload=True,
    ).points
    return [h.payload for h in hits]


def answer(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )
    prompt = f"""You are a knowledgeable technical assistant for service and maintenance documents.

Use the provided context as your primary source. When context is partial, supplement with general technical knowledge for the domain — but distinguish what comes from the loaded documents versus general practice. Never dead-end the user: if the documents lack specific detail, say what they do cover, offer general guidance, and suggest what to look for in the full manual.

Context:
{context}

Question: {question}
Answer:"""
    response = ollama.generate(model=LLM_MODEL, prompt=prompt, stream=False)
    return response["response"]


def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    client   = QdrantClient(url=QDRANT_URL)

    print(f"\nSearching for: {question}")
    chunks = retrieve(client, question)

    print("\n--- Retrieved chunks ---")
    for c in chunks:
        print(f"  [{c['source']}] ...{c['text'][:120]}...")

    print("\n--- Answer ---")
    print(answer(question, chunks))


if __name__ == "__main__":
    main()
