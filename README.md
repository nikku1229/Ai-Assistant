# AI Assistant 🤖

A powerful **local-first AI assistant** built with **React + Electron + FastAPI**, designed for real-time conversations, voice interaction, and document-aware AI responses — all running locally on your machine.

The assistant supports:

* 💬 AI-powered text chat
* 🎙️ Voice input with speech recognition
* 🔊 Spoken AI responses
* 🧠 Proactive AI-generated messages
* 📄 Document upload & semantic search (RAG)
* 💾 Persistent local chat history

---

## 🚀 Features

### 🤖 AI Chat System

* Chat with a local LLM using **Ollama**
* Powered by the `mistral` model
* Fast local inference without cloud dependency
* Context-aware responses

### 🎙️ Voice Assistant

* Speech-to-text using **Vosk**
* Microphone input with `sounddevice`
* AI voice replies using Browser Speech Synthesis (`hi-IN`)

### 📄 Document Intelligence (RAG)

* Upload PDFs/documents
* Semantic search with **ChromaDB**
* HuggingFace embeddings (`all-MiniLM-L6-v2`)
* Context-aware answers from uploaded documents

### 🧠 Proactive AI Messaging

* AI can generate proactive messages periodically
* Frontend fetches queued assistant notifications automatically

### 💾 Local Data Persistence

* Daily chat history stored in JSON files
* Local vector database storage
* Fully local-first architecture

### 🖥️ Desktop Support

* Electron wrapper support
* Can run as a desktop AI assistant

---

# 🛠️ Tech Stack

## Frontend

* React (Vite)
* Electron
* CSS
* Web Speech API

## Backend (Python)

* FastAPI
* Pydantic
* Requests
* LangChain Community
* ChromaDB
* HuggingFace Embeddings
* Vosk
* SoundDevice

## Secondary Backend

* Express.js (Optional)

## AI Runtime

* Ollama API (`localhost:11434`)
* `mistral` model

---

# 📂 Project Structure

```bash
Ai-Assistant/
│
├── Backend/              # FastAPI backend
│   ├── data/
│   │   ├── chats/
│   │   ├── docs/
│   │   └── chroma/
│   └── main.py
│
├── Frontend/             # React + Vite frontend
│   ├── src/
│   └── electron/
│
├── Js-Backend/           # Optional Express backend
│
└── package.json
```

---

# ⚙️ Prerequisites

Before running the project, install:

* Node.js & npm
* Python 3.10+
* Ollama
* `mistral` model in Ollama
* `vosk-model-en-in-0.5`
* Microphone access enabled

---

# 📥 Installation & Setup

## Clone Repository

```bash
git clone https://github.com/nikku1229/Ai-Assistant
cd ai-assistant
```

---

# 🔧 Frontend Setup

```bash
cd Frontend
npm install
```

Run frontend:

```bash
npm run start
```

---

# ⚡ Backend Setup (FastAPI)

```bash
cd Backend
pip install fastapi uvicorn pydantic requests vosk sounddevice \
langchain-community langchain-text-splitters \
langchain-chroma langchain-huggingface pypdf
```

Run backend:

```bash
python main.py
```

Backend runs on:

```bash
http://localhost:8000
```

---

# 🧩 Optional JS Backend

```bash
cd Js-Backend
npm install
npm start
```

---

# 🦙 Ollama Setup

Install Ollama and pull the `mistral` model:

```bash
ollama pull mistral
```

Start Ollama:

```bash
ollama serve
```

Default API:

```bash
http://localhost:11434
```

---

# 🎤 Vosk Model Setup

Download:

```bash
vosk-model-en-in-0.5
```

Extract the model and place it inside your local project or desktop path used in the backend.

---

# ▶️ Run Entire Project Together

From the root directory:

```bash
npm install
npm start
```

This runs:

* React frontend
* Python backend concurrently

---

# 🔌 API Endpoints

## General

```http
GET /
```

Health check endpoint.

---

## Chat

```http
POST /chat
```

Send user message and receive AI response.

---

## Voice Input

```http
GET /listen
```

Captures voice input from microphone.

---

## Proactive Messages

```http
GET /proactive
```

Fetch AI-generated proactive notifications.

---

## Document Upload

```http
POST /upload
```

Upload and index documents into vector database.

---

# 💾 Data Storage

## Chat History

```bash
Backend/data/chats/<YYYY-MM-DD>.json
```

## Uploaded Documents

```bash
Backend/data/docs/
```

## Chroma Vector Store

```bash
Backend/data/chroma/
```

---

# 🔐 Current Limitations

* Some backend paths are hardcoded for Windows
* `requirements.txt` is incomplete
* Duplicate `/upload` route exists
* No automated tests yet
* Local-only setup currently

---

# 🚀 Future Improvements

* Environment variable support
* Proper `requirements.txt`
* Docker support
* Multi-model support
* Streaming responses
* Better UI animations
* Authentication system
* Conversation memory improvements
* Mobile/Desktop packaged builds

---

# 🧠 Performance & Architecture

* Local-first architecture
* Vector-based semantic retrieval
* Lightweight embeddings model
* Persistent local storage
* Modular backend structure

---

# 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

# 👨‍💻 Author

**Nitish Sharma**

* GitHub:
  [GitHub Profile](https://github.com/nikku1229)

* LinkedIn:
  [LinkedIn Profile](https://www.linkedin.com/in/nitish-sharma-648a581b2)

---

# ⭐ Support

If you like this project:

⭐ Star the repository
🔁 Share the project
🤝 Contribute to development

---

# 🔥 Built for Local AI Experiences

A modern local AI assistant focused on privacy, voice interaction, and intelligent document understanding.
