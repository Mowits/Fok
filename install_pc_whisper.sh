#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv_whisper
source .venv_whisper/bin/activate
python -m pip install --upgrade pip
pip install faster-whisper numpy

echo "Kurulum tamam. Calistirma: source .venv_whisper/bin/activate && ./run_pc_whisper_stt.sh"
