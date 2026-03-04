#!/usr/bin/env python3
import json
import re
import socket
import time

import numpy as np
from faster_whisper import WhisperModel

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8767
TEXT_HOST = "127.0.0.1"
TEXT_PORT = 8766
SAMPLE_RATE = 16000
CHUNK_SEC = 3
BYTES_PER_CHUNK = SAMPLE_RATE * 2 * CHUNK_SEC
MIN_CHARS = 2
WAKE_WORDS = ["fok", "folk", "fox", "fog", "fort", "forum", "sol"]
WAKE_FOLLOWUP_SEC = 8


def send_text(text: str):
    payload = (json.dumps({"text": text}, ensure_ascii=True) + "\n").encode("utf-8")
    with socket.create_connection((TEXT_HOST, TEXT_PORT), timeout=3) as s:
        s.sendall(payload)


def transcribe_chunk(model: WhisperModel, pcm: bytes):
    if not pcm:
        return ""
    audio_i16 = np.frombuffer(pcm, dtype=np.int16)
    if audio_i16.size == 0:
        return ""
    # Hafif RMS kapisi
    rms = float(np.sqrt(np.mean(audio_i16.astype(np.float32) ** 2)) + 1e-6)
    if rms < 120:
        return ""
    audio = audio_i16.astype(np.float32) / 32768.0
    segments, _ = model.transcribe(audio, language="tr", vad_filter=True, beam_size=1)
    text = " ".join(s.text.strip() for s in segments if s.text).strip()
    return text


def has_wake(text: str):
    low = text.lower().replace(",", " ").replace(".", " ").replace("!", " ").replace("?", " ")
    # STT bazen "heyfok"/"heyfolk" bitisik verebiliyor
    low = low.replace("heyfok", "hey fok").replace("heyfolk", "hey folk")
    tokens = re.findall(r"[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+", low)
    token_set = set(t.lower() for t in tokens)
    return any(w in token_set for w in WAKE_WORDS)


def should_send(text: str):
    if len(text) < MIN_CHARS:
        return False
    return True


def handle_client(conn: socket.socket, model: WhisperModel):
    print("[PC-STT] Pi baglandi")
    buf = bytearray()
    conn.settimeout(10)
    wake_open_until = 0.0
    followup_available = False
    try:
        while True:
            data = conn.recv(8192)
            if not data:
                break
            buf.extend(data)
            while len(buf) >= BYTES_PER_CHUNK:
                chunk = bytes(buf[:BYTES_PER_CHUNK])
                del buf[:BYTES_PER_CHUNK]
                text = transcribe_chunk(model, chunk)
                if not text:
                    continue
                print("[PC-STT]", text)
                if not should_send(text):
                    continue

                now = time.time()
                wake_hit = has_wake(text)
                allow = False
                reason = ""
                if wake_hit:
                    allow = True
                    reason = "wake"
                    wake_open_until = now + WAKE_FOLLOWUP_SEC
                    followup_available = True
                elif followup_available and now <= wake_open_until:
                    allow = True
                    reason = "followup"
                    followup_available = False
                else:
                    print("[PC-STT] DROP (wake/followup yok)")

                if allow:
                    try:
                        send_text(text)
                        print(f"[PC-STT] SEND ok ({reason})")
                    except Exception as e:
                        print("[PC-STT] SEND fail:", e)
    except socket.timeout:
        print("[PC-STT] timeout, baglanti kapandi")
    except Exception as e:
        print("[PC-STT] hata:", e)
    finally:
        conn.close()
        print("[PC-STT] Pi ayrildi")


def main():
    print("[PC-STT] model yukleniyor...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    print(f"[PC-STT] dinlemede: {LISTEN_HOST}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((LISTEN_HOST, LISTEN_PORT))
        s.listen(1)
        while True:
            conn, _ = s.accept()
            handle_client(conn, model)
            time.sleep(0.2)


if __name__ == "__main__":
    main()
