#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y piper wget
mkdir -p "$HOME/piper_pc"
cd "$HOME/piper_pc"
wget -O tr_TR-dfki-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx
wget -O tr_TR-dfki-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx.json

echo "PC piper kuruldu. Stack: /home/mowits/Downloads/fok_modular/run_pc_stack_pc_piper.sh"
