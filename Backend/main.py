from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from datetime import datetime
from voice import listen
from proactive import start_proactive, pending_messages
from docs import add_document, search_docs

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    start_proactive()


app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# D Drive mein save hoga
CHATS_DIR = "D:\\Coding\\Project\\Self\\Ai Assistant\\Backend\\data\\chats"
os.makedirs(CHATS_DIR, exist_ok=True)

# Aaj ki chat file
today = datetime.now().strftime("%Y-%m-%d")
CHAT_FILE = os.path.join(CHATS_DIR, f"{today}.json")

# Chat history memory mein
chat_history = []

# Purani chat load karo agar aaj ki file hai
if os.path.exists(CHAT_FILE):
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                chat_history = json.loads(content)
    except:
        chat_history = []


class Message(BaseModel):
    message: str


def save_chat():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)


@app.get("/listen")
def listen_voice():
    text = listen()
    return {"text": text}


@app.post("/chat")
def chat(msg: Message):
    # Docs mein search karo
    doc_context = search_docs(msg.message)

    # Context ke saath message banao
    if doc_context:
        full_message = f"""Neeche kuch document context hai:

{doc_context}

Ab is context ko dhyan mein rakh ke is sawaal ka jawab de: {msg.message}"""
    else:
        full_message = msg.message

    chat_history.append({"role": "user", "content": full_message})

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "mistral", "messages": chat_history, "stream": False},
    )

    data = response.json()
    if "message" in data:
        print("Ollama se aaya:", data)
        ai_reply = data["message"]["content"]
    elif "response" in data:
        print("Ollama se aaya:", data)
        ai_reply = data["response"]
    else:
        print("Ollama se aaya:", data)
        ai_reply = "Kuch gadbad ho gayi, dobara pooch!"

    chat_history[-1] = {"role": "user", "content": msg.message}
    chat_history.append({"role": "assistant", "content": ai_reply})

    save_chat()
    return {"reply": ai_reply}


@app.get("/")
def root():
    return {"status": "AI Backend Chal Raha Hai!"}


@app.get("/proactive")
def get_proactive():
    if pending_messages:
        msg = pending_messages.pop(0)
        return {"message": msg}
    return {"message": None}


@app.post("/upload")
async def upload_doc(file: bytes = None):
    from fastapi import UploadFile, File

    return {"status": "ok"}


from fastapi import UploadFile, File


@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    # File save karo
    file_path = os.path.join(
        "D:\\Coding\\Project\\Self\\Ai Assistant\\backend\\data\\docs", file.filename
    )
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Document add karo
    chunks = add_document(file_path)
    return {"status": "ok", "chunks": chunks, "filename": file.filename}
