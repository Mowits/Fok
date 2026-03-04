#!/usr/bin/env python3
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 8770
FOK_TEXT_HOST = "127.0.0.1"
FOK_TEXT_PORT = 8766

state_lock = threading.Lock()
messages = []
next_seq = 1


def push_tts(text: str):
    global next_seq
    with state_lock:
        messages.append({"seq": next_seq, "text": text})
        next_seq += 1


def pull_tts(since: int):
    with state_lock:
        items = [m for m in messages if m["seq"] > since]
        cur = next_seq - 1
    return cur, items


def send_to_fok_text(text: str):
    payload = (json.dumps({"text": text}, ensure_ascii=True) + "\n").encode("utf-8")
    with socket.create_connection((FOK_TEXT_HOST, FOK_TEXT_PORT), timeout=3) as s:
        s.sendall(payload)


PAGE = """<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>FOK Phone Bridge</title>
  <style>
    body { font-family: sans-serif; margin: 16px; background: #111; color: #eee; }
    button { font-size: 18px; margin-right: 8px; padding: 10px 14px; }
    #log { white-space: pre-wrap; background: #1e1e1e; border-radius: 8px; padding: 10px; min-height: 180px; }
    .ok { color: #80ff9d; }
    .warn { color: #ffce7a; }
  </style>
</head>
<body>
  <h2>FOK Phone Audio Bridge</h2>
  <p>Screen via RealVNC, audio via this page.</p>
  <div>
    <button id=\"start\">Start Mic</button>
    <button id=\"stop\">Stop Mic</button>
  </div>
  <div style=\"margin-top:10px;\">
    <input id=\"manual\" placeholder=\"Metin girip gonder\" style=\"width:70%;font-size:16px;padding:8px;\" />
    <button id=\"send\">Gonder</button>
  </div>
  <p id=\"status\" class=\"warn\">Status: Ready</p>
  <div id=\"log\"></div>

<script>
let rec = null;
let lastSeq = 0;
const log = (t) => {
  const el = document.getElementById('log');
  el.textContent += t + "\\n";
  el.scrollTop = el.scrollHeight;
};
const status = (t, ok=false) => {
  const s = document.getElementById('status');
  s.textContent = 'Status: ' + t;
  s.className = ok ? 'ok' : 'warn';
};

async function sendSTT(text) {
  await fetch('/stt', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text})
  });
}

function startRec() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    status('SpeechRecognition not supported');
    return;
  }
  rec = new SR();
  rec.lang = 'tr-TR';
  rec.continuous = true;
  rec.interimResults = false;
  rec.onstart = () => status('Mic on', true);
  rec.onresult = async (e) => {
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (!e.results[i].isFinal) continue;
      const text = e.results[i][0].transcript.trim();
      if (!text) continue;
      log('MIC> ' + text);
      try {
        await sendSTT(text);
      } catch (err) {
        log('STT send error: ' + err);
      }
    }
  };
  rec.onerror = (e) => log('REC error: ' + e.error);
  rec.onend = () => status('Mic stopped');
  rec.start();
}

function stopRec() {
  if (rec) rec.stop();
}

function speak(text) {
  if (!('speechSynthesis' in window)) {
    log('No browser TTS: ' + text);
    return;
  }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'tr-TR';
  u.rate = 1.0;
  u.pitch = 1.0;
  speechSynthesis.speak(u);
  log('TTS> ' + text);
}

async function pollTTS() {
  try {
    const r = await fetch('/tts?since=' + lastSeq);
    const j = await r.json();
    lastSeq = j.seq || lastSeq;
    for (const item of (j.items || [])) {
      speak(item.text || '');
    }
  } catch (e) {
    log('TTS poll error: ' + e);
  }
}
setInterval(pollTTS, 1200);

document.getElementById('start').onclick = startRec;
document.getElementById('stop').onclick = stopRec;
document.getElementById('send').onclick = async () => {
  const el = document.getElementById('manual');
  const text = (el.value || '').trim();
  if (!text) return;
  try {
    await sendSTT(text);
    log('TXT> ' + text);
    el.value = '';
  } catch (err) {
    log('TXT send error: ' + err);
  }
};
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, code, text):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._html(200, PAGE)
        if u.path == "/tts":
            q = parse_qs(u.query)
            since = int((q.get("since") or ["0"])[0] or "0")
            seq, items = pull_tts(since)
            return self._json(200, {"ok": True, "seq": seq, "items": items})
        return self._json(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(n) if n > 0 else b""
        if u.path == "/stt":
            try:
                obj = json.loads(body.decode("utf-8") or "{}")
                text = (obj.get("text") or "").strip()
                if not text:
                    return self._json(400, {"ok": False, "error": "empty_text"})
                send_to_fok_text(text)
                return self._json(200, {"ok": True})
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)})
        if u.path == "/tts":
            try:
                ct = (self.headers.get("Content-Type") or "").lower()
                if "application/json" in ct:
                    obj = json.loads(body.decode("utf-8") or "{}")
                    text = (obj.get("text") or "").strip()
                else:
                    text = body.decode("utf-8").strip()
                if not text:
                    return self._json(400, {"ok": False, "error": "empty_text"})
                push_tts(text)
                return self._json(200, {"ok": True})
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)})
        return self._json(404, {"ok": False, "error": "not_found"})


def main():
    print(f"[PHONE-BRIDGE] http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
