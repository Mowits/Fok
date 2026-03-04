#!/usr/bin/env bash
set -euo pipefail

# Pi tarafinda calistirin.
# Ornek:
# FOK_PC_HOST=192.168.1.101 ./run_pi_bt.sh

export FOK_PC_HOST="${FOK_PC_HOST:-192.168.1.101}"
export FOK_PC_PORT="${FOK_PC_PORT:-8766}"
export FOK_STT_MODEL_PATH="${FOK_STT_MODEL_PATH:-/opt/vosk/vosk-model-small-tr-0.3}"
export FOK_STT_USE_ARECORD="${FOK_STT_USE_ARECORD:-0}"
export FOK_STT_DEVICE="${FOK_STT_DEVICE:-pulse}"
export FOK_STT_GAIN="${FOK_STT_GAIN:-4.0}"
export FOK_STT_CHUNK_SECONDS="${FOK_STT_CHUNK_SECONDS:-4.0}"
export FOK_STT_AGC_TARGET_RMS="${FOK_STT_AGC_TARGET_RMS:-2200}"
export FOK_STT_AGC_MAX_BOOST="${FOK_STT_AGC_MAX_BOOST:-10.0}"
export FOK_STT_NOISE_ALPHA="${FOK_STT_NOISE_ALPHA:-0.92}"
export FOK_STT_NOISE_MULT="${FOK_STT_NOISE_MULT:-1.8}"
export FOK_STT_MIN_RMS_GATE="${FOK_STT_MIN_RMS_GATE:-140}"
export FOK_STT_MIN_TEXT_CHARS="${FOK_STT_MIN_TEXT_CHARS:-2}"
export FOK_STT_SEND_ONLY_WAKE="${FOK_STT_SEND_ONLY_WAKE:-1}"
export FOK_WAKE_WORDS="${FOK_WAKE_WORDS:-fok,fox,fog,fort,forum}"
export FOK_STT_GRAMMAR_MODE="${FOK_STT_GRAMMAR_MODE:-wake}"
export FOK_STT_SOURCE_NAME="${FOK_STT_SOURCE_NAME:-}"

# Kaynak secimi:
# 1) FOK_STT_SOURCE_NAME verildiyse onu kullan.
# 2) USB mikrofon varsa onu tercih et.
# 3) Yoksa Bluetooth mikrofonu kullan.
if [ -z "${FOK_STT_SOURCE_NAME}" ]; then
  if pactl list short sources | grep -q "alsa_input.usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera_SN0001-02.analog-stereo"; then
    FOK_STT_SOURCE_NAME="alsa_input.usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera_SN0001-02.analog-stereo"
  else
    FOK_STT_SOURCE_NAME="bluez_input.40:58:99:2E:67:FC"
  fi
fi

if [[ "${FOK_STT_SOURCE_NAME}" == bluez_input* ]]; then
  pactl set-card-profile bluez_card.40_58_99_2E_67_FC headset-head-unit >/dev/null 2>&1 || true
fi

pactl set-default-source "${FOK_STT_SOURCE_NAME}" >/dev/null 2>&1 || true
pactl set-source-mute "${FOK_STT_SOURCE_NAME}" 0 >/dev/null 2>&1 || true

echo "[STT] source=${FOK_STT_SOURCE_NAME}"

if [ -f "$HOME/fok_venv/bin/activate" ]; then
  # shellcheck disable=SC1090
  source "$HOME/fok_venv/bin/activate"
fi

python /home/mowits/fok/fok_pi_stt.py
