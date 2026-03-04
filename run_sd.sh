#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Kullanim: ./run_sd.sh \"prompt metni\""
  exit 1
fi

cd /home/mowits/Downloads/fok_modular
source .venv_sd/bin/activate

PROMPT="$1"
OUT="/home/mowits/Downloads/fok_modular/outputs/sd/$(date +%Y%m%d_%H%M%S).png"
LATEST="/home/mowits/Downloads/fok_modular/outputs/sd/latest.png"
MODEL="${FOK_SD_MODEL:-runwayml/stable-diffusion-v1-5}"
STEPS="${FOK_SD_STEPS:-20}"
CFG="${FOK_SD_CFG:-7.0}"
WIDTH="${FOK_SD_WIDTH:-512}"
HEIGHT="${FOK_SD_HEIGHT:-512}"
OPEN_TARGET="${FOK_SD_OPEN_TARGET:-pc}" # pc|pi|both|none
PAUSE_LMSTUDIO="${FOK_SD_PAUSE_LMSTUDIO:-1}"
LMSTUDIO_RESTART_CMD="${FOK_LMSTUDIO_RESTART_CMD:-}"

LM_WAS_RUNNING=0
if [[ "$PAUSE_LMSTUDIO" == "1" ]]; then
  if pgrep -af 'lmstudio/.internal/utils/node|LM Studio|lmstudio' >/dev/null 2>&1; then
    LM_WAS_RUNNING=1
    pkill -f 'lmstudio/.internal/utils/node|LM Studio|lmstudio' >/dev/null 2>&1 || true
    # GPU bellek serbest kalmasi icin kisa bekleme.
    sleep 2
  fi
fi

OPEN_PC_FLAG=()
if [[ "$OPEN_TARGET" == "pc" || "$OPEN_TARGET" == "both" ]]; then
  OPEN_PC_FLAG=(--open-window)
fi

python sd_generate.py \
  --prompt "$PROMPT" \
  --negative "blurry, low quality, text, watermark, logo, deformed" \
  --model "$MODEL" \
  --steps "$STEPS" \
  --cfg "$CFG" \
  --width "$WIDTH" \
  --height "$HEIGHT" \
  --seed 42 \
  --out "$OUT" \
  "${OPEN_PC_FLAG[@]}"

cp -f "$OUT" "$LATEST"

if [[ "$OPEN_TARGET" == "pi" || "$OPEN_TARGET" == "both" ]]; then
  PI_HOST="${FOK_PI_HOST:-192.168.1.111}"
  PI_USER="${FOK_PI_USER:-mowits}"
  PI_KEY="${FOK_PI_KEY:-/home/mowits/Downloads/fok_pi_key}"
  PI_IMG="/home/${PI_USER}/Pictures/fok_latest.png"
  scp -i "$PI_KEY" -o StrictHostKeyChecking=no "$OUT" "${PI_USER}@${PI_HOST}:${PI_IMG}" >/dev/null 2>&1 || true
  ssh -i "$PI_KEY" -o StrictHostKeyChecking=no "${PI_USER}@${PI_HOST}" "mkdir -p /home/${PI_USER}/Pictures; DISPLAY=:0 xdg-open '${PI_IMG}' >/dev/null 2>&1 || true" >/dev/null 2>&1 || true
fi

if [[ "$LM_WAS_RUNNING" == "1" && -n "$LMSTUDIO_RESTART_CMD" ]]; then
  nohup bash -lc "$LMSTUDIO_RESTART_CMD" >/tmp/fok_lmstudio_restart.log 2>&1 &
fi

echo "[OK] Cikti: $OUT"
