import time
import threading
import os
import requests
from datetime import datetime
from queue import Queue, Empty
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


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


def get_context():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "subah", "Good morning bol aur kuch motivational baat kar"
    elif 12 <= hour < 17:
        return "dopahar", "Dopahar ki yaad dilao, kuch kaam ke baare mein pooch"
    elif 17 <= hour < 21:
        return "shaam", "Shaam ko aaj ka din kaisa gaya pooch"
    else:
        return "raat", "Raat ko rest karne ki yaad dilao"


def generate_message():
    time_of_day, instruction = get_context()
    model_name = os.getenv("OLLAMA_MODEL", "mistral")
    fallback_model = os.getenv("OLLAMA_FALLBACK_MODEL", "tinyllama")
    models_to_try = []
    for model in [model_name, fallback_model]:
        if model and model not in models_to_try:
            models_to_try.append(model)

    last_error = "Unknown error"
    for model in models_to_try:
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Tu ek dost hai. {instruction}. Hinglish mein 1-2 lines mein bol. Bilkul natural reh.",
                        }
                    ],
                    "stream": False,
                },
                timeout=30,
            )
            if not response.ok:
                try:
                    payload = response.json()
                    last_error = payload.get("error") or response.text
                except Exception:
                    last_error = response.text
                continue

            data = response.json()
            if "message" in data:
                return data["message"]["content"]
            return None
        except Exception as exc:
            last_error = str(exc)

    raise RuntimeError(
        f"Proactive LLM failed for models {', '.join(models_to_try)}: {last_error}"
    )


# Frontend ko message bhejne ke liye
pending_messages = Queue()


def proactive_loop():
    # Pehle 30 second wait karo — server start hone do
    time.sleep(30)

    while True:
        try:
            msg = generate_message()
            if msg:
                pending_messages.put(msg)
                print(f"Proactive message ready: {msg}")
        except Exception as e:
            print(f"Proactive error: {e}")

        # Har 30 minute mein
        time.sleep(30 * 60)


def start_proactive():
    thread = threading.Thread(target=proactive_loop, daemon=True)
    thread.start()
    print("Proactive AI chalu ho gaya!")


def pop_proactive():
    try:
        return pending_messages.get_nowait()
    except Empty:
        return None
