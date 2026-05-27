---
title: RAG Pipeline — Manual Testing Guide
tags: [testing, rag, manual]
created: 2026-05-27
---

# RAG Pipeline — Manual Testing Guide

## Prerequisites

Verify all services are running before testing:

```bash
# Ollama
curl http://localhost:11434          # expected: "Ollama is running"

# Qdrant
curl http://localhost:6333/healthz   # expected: "healthz check passed"

# Models loaded
ollama list
# expected: gemma4:latest and nomic-embed-text:latest
```

If Qdrant is not running:
```bash
podman machine start
podman start qdrant
```

---

## Setup

```bash
cd ~/data/projects/hal-ai/src/rag
source .venv/bin/activate
```

---

## Step 1 — Ingest Sample Documents

Run once. Re-running adds duplicate chunks — wipe the collection first if needed.

```bash
python3 ingest.py
```

Expected output:
```
Created collection: hal_ai_docs
  it_security_policy.txt: 3 chunks ingested
  onboarding_guide.txt:   4 chunks ingested
  vacation_policy.txt:    3 chunks ingested

Done — 10 chunks total in collection 'hal_ai_docs'
```

Verify in Qdrant dashboard: http://localhost:6333/dashboard
→ Collections → hal_ai_docs → should show 10 vectors

---

## Step 2 — Run Queries

```bash
python3 query.py "<your question>"
```

Output structure:
```
Searching for: <question>

--- Retrieved chunks ---
  [source_file.txt] ...first 120 chars of chunk...

--- Answer ---
<gemma4 grounded answer>
```

---

## Test Cases

### Vacation Policy

| Question | Expected source | Key fact in answer |
|----------|-----------------|--------------------|
| How many vacation days do new employees get? | vacation_policy.txt | 10 days per year |
| How many vacation days after 3 years? | vacation_policy.txt | 15 days per year |
| How many vacation days after 6 years? | vacation_policy.txt | 20 days per year |
| Can I carry over unused vacation? | vacation_policy.txt | Max 5 days carryover |
| Do I get paid out for vacation when I leave? | vacation_policy.txt | Yes, at current base salary |
| Can I use vacation days when I'm sick? | vacation_policy.txt | No — must use sick leave |
| How far in advance must I request vacation? | vacation_policy.txt | 5 business days |

### IT Security

| Question | Expected source | Key fact in answer |
|----------|-----------------|--------------------|
| What are the password requirements? | it_security_policy.txt | 12 chars, MFA mandatory |
| How often must I change my password? | it_security_policy.txt | Every 90 days |
| Do I need VPN at a coffee shop? | it_security_policy.txt | Yes, always |
| What do I do if I lose my laptop? | it_security_policy.txt | Report to security@company.com / ext 9911 |
| Can I install software on my work laptop? | it_security_policy.txt | No — submit request via helpdesk |
| Will IT ever ask for my password? | it_security_policy.txt | No — never |

### Onboarding

| Question | Expected source | Key fact in answer |
|----------|-----------------|--------------------|
| What time do I arrive on day one? | onboarding_guide.txt | 9:00 AM at reception |
| How long to enroll in benefits? | onboarding_guide.txt | 30 days from start |
| When does payroll run? | onboarding_guide.txt | Bi-weekly on Fridays |
| How do I set up direct deposit? | onboarding_guide.txt | HR portal, within first week |
| What is a buddy? | onboarding_guide.txt | Peer with 1+ year tenure |
| Who do I call for urgent IT issues? | onboarding_guide.txt | ext 4100 |

### Cross-Document Retrieval

These verify the vector search picks the correct document when multiple docs are relevant:

```bash
python3 query.py "What is the security hotline number?"
# Expected: ext 9911 — from it_security_policy.txt

python3 query.py "What happens to my vacation if I resign?"
# Expected: paid out at base salary — from vacation_policy.txt

python3 query.py "What mandatory training is required in week one?"
# Expected: LMS modules — from onboarding_guide.txt
```

### Negative Tests — Out of Scope

These questions have no answer in the ingested documents.
Expected: model says it doesn't have the information.

```bash
python3 query.py "What is the remote work policy?"
python3 query.py "How do I apply for a promotion?"
python3 query.py "What is the company's parental leave policy?"
python3 query.py "How do I expense a business meal?"
```

Pass criteria: answer does NOT hallucinate a policy. Should say something like:
> "I don't have that information in the provided documents."

---

## Wiping and Re-ingesting

If you need a clean slate (e.g. after changing chunk settings):

```bash
python3 - <<'EOF'
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
client.delete_collection("hal_ai_docs")
print("Collection deleted.")
EOF

python3 ingest.py
```

---

## Adding New Documents

Drop any `.txt` file into `src/rag/sample_docs/` and re-run `ingest.py`.
Existing chunks are not deduped — delete the collection first if re-ingesting the same file.

PDF and DOCX support comes in the ingestion pipeline epic (`hal-ai-zqf.1.1`, `hal-ai-zqf.1.2`).

---

## Qdrant Dashboard

| URL | Purpose |
|-----|---------|
| http://localhost:6333/dashboard | Browse collections, inspect vectors |
| http://localhost:6333/collections | REST — list all collections |
| http://localhost:6333/collections/hal_ai_docs | REST — collection stats |
