import json
import socket


def send_pi_command(host: str, port: int, payload: dict) -> None:
    data = (json.dumps(payload, ensure_ascii=True) + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=3) as s:
        s.sendall(data)
