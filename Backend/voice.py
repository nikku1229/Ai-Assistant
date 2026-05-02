import sounddevice as sd
import vosk
import json
import queue
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "vosk-model-en-in-0.5"

# Model ek baar load hoga — server start pe
print("Voice model load ho raha hai...")
model = vosk.Model(str(MODEL_PATH))
print("Voice model ready!")

audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))


def listen(timeout=10):
    # Queue saaf karo pehle
    while not audio_queue.empty():
        audio_queue.get()

    rec = vosk.KaldiRecognizer(model, 16000)
    result_text = ""

    try:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            print("Sun raha hoon...")

            start = time.time()

            while True:
                # Timeout check
                if time.time() - start > timeout:
                    print("Timeout — kuch nahi suna")
                    break

                if not audio_queue.empty():
                    data = audio_queue.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        result_text = result.get("text", "")
                        if result_text:
                            print(f"Suna: {result_text}")
                            break

    except Exception as e:
        print(f"Voice error: {e}")

    return result_text
