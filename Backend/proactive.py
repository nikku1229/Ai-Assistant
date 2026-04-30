import time
import threading
import requests
from datetime import datetime


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

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "mistral",
            "messages": [
                {
                    "role": "user",
                    "content": f"Tu ek dost hai. {instruction}. Hinglish mein 1-2 lines mein bol. Bilkul natural reh.",
                }
            ],
            "stream": False,
        },
    )

    data = response.json()
    if "message" in data:
        return data["message"]["content"]
    return None


# Frontend ko message bhejne ke liye
pending_messages = []


def proactive_loop():
    # Pehle 30 second wait karo — server start hone do
    time.sleep(30)

    while True:
        try:
            msg = generate_message()
            if msg:
                pending_messages.append(msg)
                print(f"Proactive message ready: {msg}")
        except Exception as e:
            print(f"Proactive error: {e}")

        # Har 30 minute mein
        time.sleep(30 * 60)


def start_proactive():
    thread = threading.Thread(target=proactive_loop, daemon=True)
    thread.start()
    print("Proactive AI chalu ho gaya!")
