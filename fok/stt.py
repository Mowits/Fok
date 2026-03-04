import json
import socket
import threading
import queue


def try_init_whisper(cfg: dict):
    if not cfg.get("stt_enabled", False):
        return None
    try:
        import whisper
        import sounddevice as sd
        import numpy as np
    except Exception:
        return None

    model_name = cfg.get("stt_model", "small")
    device = cfg.get("stt_device", None)
    sample_rate = int(cfg.get("stt_sample_rate", 16000))
    chunk = float(cfg.get("stt_chunk_seconds", 3.0))
    model = whisper.load_model(model_name)

    def record_once():
        duration = chunk
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            device=device,
        )
        sd.wait()
        return np.squeeze(audio)

    def transcribe_once():
        audio = record_once()
        result = model.transcribe(audio, language=cfg.get("stt_language", "tr"), fp16=False)
        return (result.get("text") or "").strip()

    return transcribe_once


def start_remote_stt_server(cfg: dict, text_queue: queue.Queue):
    host = cfg.get("remote_stt_listen", "0.0.0.0")
    port = int(cfg.get("remote_stt_port", 8766))

    def client_thread(conn):
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                while b"\n" in data:
                    line, data = data.split(b"\n", 1)
                    if not line:
                        continue
                    try:
                        text = line.decode("utf-8").strip()
                        if text.startswith("{"):
                            obj = json.loads(text)
                            text = obj.get("text", "").strip()
                        if text:
                            text_queue.put(text)
                    except Exception:
                        continue
        finally:
            conn.close()

    def server_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(5)
            print(f"[STT] Remote dinlemede: {host}:{port}")
            while True:
                conn, _ = s.accept()
                t = threading.Thread(target=client_thread, args=(conn,), daemon=True)
                t.start()

    t = threading.Thread(target=server_thread, daemon=True)
    t.start()
    return True
