from pathlib import Path
import json
import os
import re
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from voice import listen
from proactive import start_proactive, pop_proactive
from docs import add_document, search_docs, DOCS_DIR

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    start_proactive()


app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

BASE_DIR = Path(__file__).resolve().parent
CHATS_DIR = BASE_DIR / "data" / "chats"
CHATS_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE = BASE_DIR / "data" / "user_memory.json"


def load_local_env():
    env_path = BASE_DIR.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "tinyllama")

# Aaj ki chat file
today = datetime.now().strftime("%Y-%m-%d")
CHAT_FILE = CHATS_DIR / f"{today}.json"

# Chat history memory mein
chat_history = []

# Purani chat load karo agar aaj ki file hai
if CHAT_FILE.exists():
    try:
        with CHAT_FILE.open("r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                chat_history = json.loads(content)
    except:
        chat_history = []


def sanitize_chat_history(items):
    cleaned = []
    for item in items:
        role = item.get("role")
        content = str(item.get("content", "")).strip()
        if role not in {"user", "assistant"} or not content:
            continue
        if role == "assistant" and len(content) > 500:
            continue
        cleaned.append({"role": role, "content": content})
    return cleaned[-100:]


chat_history = sanitize_chat_history(chat_history)


class Message(BaseModel):
    message: str


class MemoryUpdate(BaseModel):
    name: str | None = None
    add_facts: list[str] = []
    clear_facts: bool = False


def load_user_memory():
    if not MEMORY_FILE.exists():
        return {"name": "", "facts": []}
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"name": "", "facts": []}
        name = data.get("name", "")
        facts = data.get("facts", [])
        if not isinstance(facts, list):
            facts = []
        return {"name": str(name).strip(), "facts": [str(f).strip() for f in facts if f]}
    except Exception:
        return {"name": "", "facts": []}


def save_user_memory(memory):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")


def add_fact(memory, fact):
    fact = fact.strip()
    if not fact:
        return
    existing = {f.lower(): f for f in memory["facts"]}
    if fact.lower() not in existing:
        memory["facts"].append(fact)
    memory["facts"] = memory["facts"][-25:]


def tokenize_for_match(text):
    return set(re.findall(r"[a-zA-Z]{3,}", text.lower()))


def looks_offtopic(user_text, reply_text):
    user_tokens = tokenize_for_match(user_text)
    reply_tokens = tokenize_for_match(reply_text)
    if len(user_tokens) < 2:
        return False
    return len(user_tokens.intersection(reply_tokens)) == 0


def answer_from_memory_if_possible(user_text):
    lowered = user_text.lower()
    asks_name = (
        "mera naam" in lowered
        or "my name" in lowered
        or "tumhe mera naam" in lowered
        or "what is my name" in lowered
    )
    if not asks_name:
        return None
    memory = load_user_memory()
    name = memory.get("name", "").strip()
    if name:
        return f"Tumhara naam {name} hai."
    return "Abhi tumhara naam saved nahi hai. Bolo: my name is <naam>."


def sanitize_memory(memory):
    name = str(memory.get("name", "")).strip()
    facts = memory.get("facts", [])
    if not isinstance(facts, list):
        facts = []
    clean_facts = []
    seen = set()
    for fact in facts:
        text = str(fact).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        clean_facts.append(text)
    return {"name": name, "facts": clean_facts[-25:]}


def update_user_memory_from_text(user_text):
    text = user_text.strip()
    if not text:
        return

    memory = load_user_memory()
    lowered = text.lower()

    name_match = re.search(r"(?:my name is|mera naam)\s+([a-zA-Z][a-zA-Z ]{1,30})", lowered)
    if name_match:
        guessed_name = name_match.group(1).strip().title()
        if guessed_name and len(guessed_name.split()) <= 3:
            memory["name"] = guessed_name

    pref_match = re.search(r"(?:i like|mujhe)\s+(.+?)(?:\.$|$)", text, flags=re.IGNORECASE)
    if pref_match:
        add_fact(memory, f"Preference: {pref_match.group(1).strip()}")

    remember_match = re.search(
        r"(?:remember that|yaad rakhna)\s+(.+?)(?:\.$|$)",
        text,
        flags=re.IGNORECASE,
    )
    if remember_match:
        add_fact(memory, f"Important: {remember_match.group(1).strip()}")

    save_user_memory(memory)


def save_chat():
    with CHAT_FILE.open("w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)


def request_ollama_with_fallback(messages):
    models_to_try = []
    for model in [OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL]:
        if model and model not in models_to_try:
            models_to_try.append(model)

    errors = []
    for model in models_to_try:
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.35, "top_p": 0.9},
                },
                timeout=60,
            )
            if response.ok:
                return response.json(), model
            try:
                err_payload = response.json()
                err_msg = err_payload.get("error") or response.text
            except Exception:
                err_msg = response.text
            errors.append(f"{model}: {err_msg}")
        except Exception as exc:
            errors.append(f"{model}: {exc}")

    raise HTTPException(
        status_code=503,
        detail=f"Local LLM failed. Tried {', '.join(models_to_try)}. Errors: {' | '.join(errors)}",
    )


@app.get("/listen")
def listen_voice():
    text = listen()
    return {"text": text}


@app.post("/chat")
def chat(msg: Message):
    user_text = msg.message.strip()
    update_user_memory_from_text(user_text)
    direct_memory_reply = answer_from_memory_if_possible(user_text)
    if direct_memory_reply:
        chat_history.append({"role": "user", "content": user_text})
        chat_history.append({"role": "assistant", "content": direct_memory_reply})
        save_chat()
        return {"reply": direct_memory_reply}

    doc_context = search_docs(user_text)
    memory = load_user_memory()
    memory_lines = []
    if memory.get("name"):
        memory_lines.append(f"User name: {memory['name']}")
    for fact in memory.get("facts", [])[-10:]:
        memory_lines.append(f"- {fact}")
    memory_block = "\n".join(memory_lines) if memory_lines else "No saved memory yet."

    system_prompt = (
        "You are a local personal AI assistant.\n"
        "Rules:\n"
        "1) User ke exact sawal ka hi jawab do.\n"
        "2) Short practical Hinglish (max 2-3 lines).\n"
        "3) Unrelated essay/examples/roleplay mat do.\n"
        "4) Agar unsure ho to ek short clarification pucho.\n\n"
        f"Known user memory:\n{memory_block}"
    )

    messages_for_model = [{"role": "system", "content": system_prompt}]
    if doc_context:
        messages_for_model.append(
            {
                "role": "system",
                "content": f"Relevant document context:\n{doc_context}",
            }
        )

    recent_history = []
    for item in chat_history[-20:]:
        content = str(item.get("content", "")).strip()
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue
        if role == "assistant" and len(content) > 500:
            continue
        recent_history.append({"role": role, "content": content})
    recent_history = recent_history[-8:]
    messages_for_model.extend(recent_history)
    messages_for_model.append({"role": "user", "content": user_text})

    try:
        data, used_model = request_ollama_with_fallback(messages_for_model)
        print(f"Using model: {used_model}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Local LLM service unavailable: {exc}"
        ) from exc

    if "message" in data:
        print("Ollama se aaya:", data)
        ai_reply = data["message"]["content"]
    elif "response" in data:
        print("Ollama se aaya:", data)
        ai_reply = data["response"]
    else:
        print("Ollama se aaya:", data)
        ai_reply = "Kuch gadbad ho gayi, dobara pooch!"

    ai_reply = str(ai_reply).strip()
    if len(ai_reply) > 350:
        ai_reply = ai_reply[:350].rsplit(" ", 1)[0] + "..."
    if looks_offtopic(user_text, ai_reply):
        ai_reply = "Main drift ho gaya tha. Ek line me dobara pucho, main seedha exact jawab dunga."

    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": ai_reply})

    save_chat()
    return {"reply": ai_reply}


@app.get("/")
def root():
    return {"status": "AI Backend Chal Raha Hai!"}


@app.get("/proactive")
def get_proactive():
    return {"message": pop_proactive()}


@app.get("/memory")
def get_memory():
    return sanitize_memory(load_user_memory())


@app.post("/memory")
def update_memory(payload: MemoryUpdate):
    memory = load_user_memory()
    if payload.clear_facts:
        memory["facts"] = []
    if payload.name is not None:
        memory["name"] = payload.name.strip()
    for fact in payload.add_facts:
        add_fact(memory, fact)
    memory = sanitize_memory(memory)
    save_user_memory(memory)
    return {"status": "ok", "memory": memory}


@app.delete("/memory")
def clear_memory():
    memory = {"name": "", "facts": []}
    save_user_memory(memory)
    return {"status": "ok", "memory": memory}


@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    safe_name = Path(file.filename or "").name
    if not safe_name or safe_name != (file.filename or ""):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not re.fullmatch(r"[\w.\- ]+", safe_name):
        raise HTTPException(status_code=400, detail="Filename contains invalid chars")

    file_path = DOCS_DIR / safe_name
    size = 0
    max_bytes = 10 * 1024 * 1024  # 10MB cap for local stability
    with file_path.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                file_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large (max 10MB)")
            f.write(chunk)

    # Document add karo
    chunks = add_document(str(file_path))
    return {"status": "ok", "chunks": chunks, "filename": safe_name}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
