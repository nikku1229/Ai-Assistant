# AI Assistant

A local-first AI assistant project with a React/Electron frontend and a FastAPI backend.

It supports text chat, voice input, spoken AI replies, proactive assistant messages, and document-aware answers using vector search (RAG-like context injection).

## Features

- Chat with a local LLM (via Ollama, `mistral` model in current code).
- Voice input using Vosk + microphone capture.
- Voice output in browser using Speech Synthesis (`hi-IN`).
- Proactive AI messages generated periodically and fetched by the frontend.
- Document upload and semantic retrieval with Chroma + HuggingFace embeddings.
- Daily chat history persistence in JSON files.

## Tech Stack

- **Frontend**
  - React
  - Vite
  - Electron (desktop wrapper)

- **Backend (Python)**
  - FastAPI
  - Pydantic
  - Requests
  - LangChain community tools
  - Chroma vector database
  - HuggingFace embeddings (`all-MiniLM-L6-v2`)
  - Vosk + sounddevice (speech recognition)

- **Secondary Backend (Node)**
  - Express 5 (in `Js-Backend`, optional/minimal)

- **LLM Runtime**
  - Ollama API on `http://localhost:11434`

## Project Structure

```text
Ai Assistant/
├─ Backend/          # FastAPI app, voice, proactive, docs retrieval
├─ Frontend/         # React + Vite app, optional Electron wrapper
├─ Js-Backend/       # Minimal Express backend (separate/optional)
└─ package.json      # Root scripts to run frontend + backend together
```

## Prerequisites

- Node.js and npm
- Python 3.10+ (recommended)
- Ollama model running locally with the `mistral` model available
- Microphone access (for voice input)
- Download Ollama with `mistral` model adn also `vosk-model-en-in-0.5` on the local desktop to run

## Installation

From the repository root:

```bash
npm install
```

Install frontend dependencies:

```bash
cd Frontend
npm install
```

Install JS backend dependencies (optional):

```bash
cd ../Js-Backend
npm install
```

Install Python backend dependencies manually (current `requirements.txt` is empty):

```bash
cd ../Backend
pip install fastapi uvicorn pydantic requests vosk sounddevice langchain-community langchain-text-splitters langchain-chroma langchain-huggingface pypdf
```

## Running the App

### Option 1: Run from root (frontend + Python backend together)

```bash
npm start
```

This runs:

- Frontend dev server (`Frontend`, Vite)
- Python backend (`Backend/main.py`) on port `8000`

### Option 2: Run services manually

Optional Electron mode:

```bash
cd Frontend
npm run start
```

Python backend:

```bash
cd Backend
python main.py
```

Optional Frontend:

```bash
cd Frontend
npm run dev
```

## API Overview (FastAPI backend)

- `GET /` - health/status
- `POST /chat` - send user message and receive AI reply
- `GET /listen` - capture voice input and return recognized text
- `GET /proactive` - fetch queued proactive message (if available)
- `POST /upload` - upload document and index it into vector store

## Data and Storage

- Chat history: `Backend/data/chats/<YYYY-MM-DD>.json`
- Uploaded docs: `Backend/data/docs/`
- Chroma vector store: `Backend/data/chroma/`

## Notes and Current Limitations

- Several backend paths are hardcoded as absolute Windows paths.
- `Backend/requirements.txt` is currently empty.
- There is a duplicate `/upload` route definition in `Backend/main.py`; the second one is the effective handler.
- No automated tests are configured yet.

## Suggested Next Improvements

- Move all hardcoded paths and model names to environment variables.
- Add a proper `requirements.txt` and setup script.
- Add unit/integration tests for chat, voice, and document pipelines.
- Add Docker support for reproducible setup.
