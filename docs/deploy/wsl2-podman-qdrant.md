---
title: WSL2 + Podman + Qdrant Setup
tags: [deploy, install, wsl2, podman, qdrant]
---

# WSL2 + Podman + Qdrant Setup

## 1. Enable WSL2 on Windows Server

Run in PowerShell (Administrator):

```powershell
wsl --install -d Ubuntu-22.04
wsl --set-default-version 2
```

Restart when prompted. After restart, Ubuntu launches and asks for a username/password.

Verify:
```powershell
wsl --list --verbose
# NAME            STATE   VERSION
# Ubuntu-22.04    Running 2
```

---

## 2. Install Podman inside WSL2

Open Ubuntu terminal:

```bash
sudo apt update && sudo apt install -y podman

# Verify — no 'podman machine init' needed in WSL2
podman --version
```

---

## 3. Run Qdrant

```bash
podman run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $HOME/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant:latest
```

Verify:
```bash
curl http://localhost:6333/healthz
# healthz check passed
```

Also verify from Windows (PowerShell or browser):
```
http://localhost:6333/healthz
```
WSL2 automatically forwards ports to the Windows host.

---

## 4. Auto-start Qdrant on WSL2 boot

Check if systemd is running:
```bash
ps -p 1 -o comm=
# systemd  ← good
# init     ← use fallback method below
```

**With systemd** (WSL2 ≥ 0.67.6):
```bash
podman generate systemd --name qdrant --files --new
sudo mv container-qdrant.service /etc/systemd/system/
sudo systemctl enable --now container-qdrant.service
sudo systemctl status container-qdrant.service
```

**Without systemd** — add to `~/.bashrc`:
```bash
echo 'podman start qdrant 2>/dev/null || true' >> ~/.bashrc
```

---

## 5. Air-gap install (no internet)

If the machine has no internet access, load the image from the bundle:

```bash
# Transfer docs/src/docker-images/qdrant.tar.gz to the machine first
podman load < docs/src/docker-images/qdrant.tar.gz
podman images    # confirm qdrant image is listed
```

Then run Step 3 as normal.

---

## Manage Qdrant

```bash
podman stop qdrant      # stop
podman start qdrant     # start
podman restart qdrant   # restart
podman logs qdrant      # view logs
podman rm -f qdrant     # delete container (data in ~/qdrant_storage is preserved)
```
