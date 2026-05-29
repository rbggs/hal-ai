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


