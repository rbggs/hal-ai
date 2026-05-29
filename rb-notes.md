This is Ramesh Babu's notes

# Install ollama 
- sudo apt-get install zstd
- `curl -fsSL https://ollama.com/install.sh | sh
- ollama pull nomic-embed-text:latest   
- ollama pull gemma4:latest
- ollama list 


# install podman & qdrant
- wipe the whole DB clean
- remove any specific documents

## install podman 
- sudo apt update 
- sudo apt install -y podman 
- podman --version 

## install Qdrant
- podman pull docker.io/qdrant/qdrant:latest 
- mkdir ~/qdrant_storage

podman run -d \
--name qudrant \
-p 6333:6333 \
-p 6334:6334 \
-v ~/qdrant_storage:/qdrant/storage:z \
docker.io/qdrant/qdrant:latest 

- podman ps
- curl http://localhost:6333
- curk http://localhost:6334/collections




# install get code from github and run the applicaiton 



# ingestion pipleline 



# testing questions




# Advance testing 
 ---
  Quick connectivity check (just verify both are running):
  curl http://localhost:11434/api/tags        # Ollama
  curl http://localhost:6333/healthz          # Qdrant

  ---
  End-to-end RAG test (embedding + retrieval + generation):
  python src/rag/query.py "your question here"
  This tests the full pipeline — Ollama embeddings → Qdrant retrieval → Ollama LLM answer.

  ---
  Start all services + health checks in one shot:
  bash scripts/start.sh
  Starts Ollama, Qdrant, and Chainlit, with built-in waits until each is healthy.

  ---
  Reset Qdrant collection (if you want a clean slate):
  python scripts/qdrant_reset.py

  The most useful for a quick sanity check is python src/rag/query.py "test question" — it exercises both services end to end




-  pip install ollama qdrant-client pdfplumber


 python3 -m venv .venv
  source .venv/bin/activate
  pip install -r src/rag/requirements.txt -r src/ui/requirements.txt


--  pip install -r src/rag/requirements.txt -r src/ui/requirements.txt

Ingest everything in the ingestions/ folder:
  src/rag/ingest.py

  Ingest a specific PDF:
  src/rag/ingest.py ingestions/your-file.pdf

  Ingest a specific XML:
  src/rag/ingest.py ingestions/your-file.xml

  Reset Qdrant collection (wipe clean before re-ingesting):
  scripts/qdrant_reset.py
  src/rag/ingest.py




# Questions for testing : 
 Catalytic Converter:
  1. What tools are required to remove the catalytic converter?
  2. What is the torque specification for the mounting bolt on the catalytic converter?
  3. Why do two or more people need to be present during catalytic converter removal?
  4. What is the part number for the catalytic converter?
  5. What should you inspect on the gasket after removing the catalytic converter?
  6. What lubricant should be applied to the U-bolt threads before installation?

  EATS ACM Harness:
  7. How long does the EATS ACM harness removal and installation take?
  8. What tool is used to loosen the urea dust cover wing nut?
  9. What is the part number for the ACM harness?
  10. What pre-removal steps must be done before handling the urea tank components?




testing : 
- src/tests/query_test.py "tell me a joke"




