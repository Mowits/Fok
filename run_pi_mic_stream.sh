#!/usr/bin/env bash
set -euo pipefail

PC_HOST="${FOK_PC_HOST:-192.168.1.101}"
PC_PORT="${FOK_PC_AUDIO_PORT:-8767}"
SRC="${FOK_PI_SOURCE:-pulse}"

# Ayni anda hem bu script hem eski Pi STT calisirse cift ses/komut olur.
pkill -f fok_pi_stt.py >/dev/null 2>&1 || true

# Pi mikrofonunu ham PCM olarak PC'ye aktarir.
while true; do
  arecord -D "$SRC" -f S16_LE -r 16000 -c 1 -t raw 2>/dev/null | nc "$PC_HOST" "$PC_PORT" || true
  sleep 1
done
