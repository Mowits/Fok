#!/usr/bin/env bash
set -euo pipefail

cd /home/mowits/Downloads/fok_modular
python3 -m venv .venv_sd
source .venv_sd/bin/activate
python -m pip install --upgrade pip

# RTX 4060 icin once CUDA 12.4 wheel denenir, olmazsa varsayilan wheel'e duser.
if ! pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124; then
  pip install torch torchvision
fi

# Diffusers ile uyumlu stabil surumler (transformers 5.x bazi importlari bozuyor)
pip install "transformers<5" "diffusers==0.31.0" "huggingface_hub<1.0" accelerate safetensors pillow sentencepiece

echo "[OK] SD ortam hazir: /home/mowits/Downloads/fok_modular/.venv_sd"
echo "[KULLANIM]"
echo "cd /home/mowits/Downloads/fok_modular"
echo "source .venv_sd/bin/activate"
echo "python sd_generate.py --prompt \"futuristic rescue robot, cinematic, ultra detailed\""
