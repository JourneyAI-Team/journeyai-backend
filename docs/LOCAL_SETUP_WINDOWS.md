# JourneyAI Local Development Setup (Windows)

This guide will help you set up the JourneyAI backend for local development on Windows, starting from installing WSL2, Docker Desktop, and all required dependencies.

---

## 1. Install WSL2 (Windows Subsystem for Linux 2)


1. Open PowerShell as Administrator and run:
   ```powershell
   wsl --install Ubuntu
   ```
   This will install WSL2 and the latest Ubuntu distribution in one step.
2. Restart your computer if prompted.
3. Launch Ubuntu from your Start menu. On first launch, set up your username and password as prompted.

More details: https://docs.microsoft.com/en-us/windows/wsl/install

---

## 2. Install Docker Desktop

1. Download Docker Desktop for Windows: https://www.docker.com/products/docker-desktop
2. Install Docker Desktop and enable WSL2 integration during setup.
3. Start Docker Desktop and ensure it is running.

---

## 3. Install Git

Download and install Git for Windows: https://git-scm.com/download/win

---

## 4. Clone the JourneyAI Repository


 run:

```powershell
git clone https://github.com/JourneyAI-Team/journeyai-backend.git
cd journeyai-backend
```

---

## 5. Install Python 3.10+ and pip (in WSL2)
Open your Ubuntu (WSL2) terminal with : 
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

---

## 6. Install Poetry (Python dependency manager)

```bash
pip3 install --user poetry

```

---

## 7. Install Make (in WSL2)

```bash
sudo apt install make -y
```

---

## 8. Install Project Dependencies

```bash
poetry install
```

---

## 9. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   make setup-local
   ```
2. Edit `.env.local` and add your API keys (OpenAI, Groq, Search1API, etc.)

---

## 10. Start Infrastructure Services and Application

```bash
make run-local
```

- This will start MongoDB, Redis, and Qdrant in Docker containers, and run the FastAPI app and background workers locally.

---

## 11. Access the Application

- API: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

---

## 12. Stopping Services

```bash
make stop-local
# or
docker compose -f docker-compose.local.yaml down
```

---

## Troubleshooting

- If you get Docker permission errors in WSL2, add your user to the docker group:
  ```bash
  sudo usermod -aG docker $USER
  # Then restart your WSL2 terminal
  ```
- If you see errors about missing Python packages (like `honcho` or `arq`), run:
  ```bash
  poetry install
  ```

---

You are now ready to develop and test JourneyAI locally on Windows using WSL2!
