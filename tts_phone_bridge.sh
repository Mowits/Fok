#!/usr/bin/env bash
set -euo pipefail
TEXT="${1:-}"
[ -z "$TEXT" ] && exit 0
PORT="${FOK_PHONE_BRIDGE_PORT:-8770}"
if command -v curl >/dev/null 2>&1; then
  curl -sS -X POST "http://127.0.0.1:${PORT}/tts" -H 'Content-Type: application/json' -d "{\"text\":$(printf '%s' "$TEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')}" >/dev/null
fi
