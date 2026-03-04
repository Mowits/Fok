#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip portaudio19-dev alsa-utils pulseaudio-utils

python3 -m venv "$HOME/fok_venv"
source "$HOME/fok_venv/bin/activate"
python -m pip install --upgrade pip
pip install sounddevice vosk numpy

echo "Pi kurulum tamam."
