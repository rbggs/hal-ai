#!/usr/bin/env python3
"""Manual query tester for the HAL-AI RAG pipeline.

Usage:
    src/tests/query_test.py "your question here"   # single question
    src/tests/query_test.py --all                  # run all predefined questions
"""
import sys
import time
from pathlib import Path

# allow importing from src/rag
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rag"))
from query import answer, retrieve  # noqa: E402
from qdrant_client import QdrantClient  # noqa: E402

QDRANT_URL = "http://localhost:6333"

# ── ANSI colours ──────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"
DIM    = "\033[2m"

SEP  = "=" * 64
SEP2 = "-" * 64

# ── Predefined test questions ─────────────────────────────────
TEST_QUESTIONS = [
    "Tell me a joke",
    "What tools are required to remove the catalytic converter?",
    "What is the torque specification for the mounting bolt on the catalytic converter?",
    "Why do two or more people need to be present during catalytic converter removal?",
    "What is the part number for the catalytic converter?",
    "What should you inspect on the gasket after removing the catalytic converter?",
    "What lubricant should be applied to the U-bolt threads before installation?",
    "How long does the EATS ACM harness removal and installation take?",
    "What tool is used to loosen the urea dust cover wing nut?",
    "What is the part number for the ACM harness?",
    "What pre-removal steps must be done before handling the urea tank components?",
]


def run_query(client: QdrantClient, question: str, index: int = 1, total: int = 1):
    print(f"\n{SEP}")
    print(f"{BOLD}{YELLOW}  Q{index}/{total}: {question}{RESET}")
    print(SEP2)

    # Retrieve
    t0 = time.time()
    try:
        chunks = retrieve(client, question)
    except Exception as e:
        print(f"{RED}  ❌ Retrieval error: {e}{RESET}")
        return
    retrieval_ms = (time.time() - t0) * 1000

    # Show chunks
    print(f"{CYAN}{BOLD}  Retrieved chunks ({len(chunks)}):{RESET}")
    for i, c in enumerate(chunks, 1):
        source  = c.get("source", "unknown")
        title   = c.get("title", "")
        snippet = c.get("text", "")[:150].replace("\n", " ")
        print(f"{DIM}  [{i}] {source}  |  {title}{RESET}")
        print(f"      {snippet}...")

    print(SEP2)

    # Generate answer
    print(f"{BOLD}  Generating answer...{RESET}")
    t1 = time.time()
    try:
        response = answer(question, chunks)
    except Exception as e:
        print(f"{RED}  ❌ LLM error: {e}{RESET}")
        return
    llm_ms = (time.time() - t1) * 1000

    print(f"\n{GREEN}{BOLD}  Answer:{RESET}")
    for line in response.strip().splitlines():
        print(f"{GREEN}  {line}{RESET}")

    print(f"\n{DIM}  ⏱  Retrieval: {retrieval_ms:.0f}ms  |  LLM: {llm_ms:.0f}ms  |  Total: {retrieval_ms+llm_ms:.0f}ms{RESET}")


def main():
    client = QdrantClient(url=QDRANT_URL)

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        print(f"\n{BOLD}{SEP}{RESET}")
        print(f"{BOLD}  HAL-AI RAG  —  Running {len(TEST_QUESTIONS)} test questions{RESET}")
        print(f"{BOLD}{SEP}{RESET}")
        for i, q in enumerate(TEST_QUESTIONS, 1):
            run_query(client, q, index=i, total=len(TEST_QUESTIONS))
        print(f"\n{SEP}")
        print(f"{BOLD}  ✅  All {len(TEST_QUESTIONS)} questions complete{RESET}")
        print(f"{SEP}\n")

    elif len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        run_query(client, question, index=1, total=1)
        print(f"\n{SEP}\n")

    else:
        print(f"Usage:")
        print(f'  src/tests/query_test.py "your question"')
        print(f'  src/tests/query_test.py --all')
        sys.exit(1)


if __name__ == "__main__":
    main()
