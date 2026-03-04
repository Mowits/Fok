#!/usr/bin/env python3
import argparse
import os
import subprocess
import time
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Stable Diffusion gorsel uretimi (RTX 4060 odakli, fallback CPU)."
    )
    p.add_argument("--prompt", required=True, help="Pozitif prompt")
    p.add_argument(
        "--negative",
        default="blurry, low quality, worst quality, text, watermark",
        help="Negatif prompt",
    )
    p.add_argument(
        "--model",
        default="stabilityai/sdxl-turbo",
        help="HuggingFace model id (ornek: stabilityai/sdxl-turbo)",
    )
    p.add_argument("--steps", type=int, default=8, help="Inference step")
    p.add_argument("--cfg", type=float, default=1.5, help="Guidance scale")
    p.add_argument("--width", type=int, default=1024, help="Genislik")
    p.add_argument("--height", type=int, default=576, help="Yukseklik")
    p.add_argument("--seed", type=int, default=42, help="Deterministik seed")
    p.add_argument(
        "--out",
        default="/home/mowits/Downloads/fok_modular/outputs/sd/latest.png",
        help="Cikti dosya yolu",
    )
    p.add_argument(
        "--open-window",
        action="store_true",
        help="Uretim bittiginde gorseli pencere olarak ac",
    )
    return p.parse_args()


def main():
    args = parse_args()
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    import torch
    from diffusers import AutoPipelineForText2Image

    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        torch.backends.cuda.matmul.allow_tf32 = True
        free_mem, total_mem = torch.cuda.mem_get_info()
        free_gb = free_mem / (1024**3)
        total_gb = total_mem / (1024**3)
        print(f"[SD] VRAM free/total: {free_gb:.2f}GB / {total_gb:.2f}GB")
        if free_gb < 5.5:
            print("[SD] UYARI: Bos VRAM dusuk. SD icin LM Studio gibi GPU uygulamalarini kapat.")
    else:
        device = "cpu"
        dtype = torch.float32

    print(f"[SD] model={args.model}")
    print(f"[SD] device={device} dtype={dtype} steps={args.steps} cfg={args.cfg}")
    print(f"[SD] size={args.width}x{args.height} seed={args.seed}")

    pipe = AutoPipelineForText2Image.from_pretrained(
        args.model,
        torch_dtype=dtype,
        use_safetensors=True,
    )
    use_offload = False
    if device == "cuda":
        free_mem, total_mem = torch.cuda.mem_get_info()
        free_gb = free_mem / (1024**3)
        total_gb = total_mem / (1024**3)
        print(f"[SD] VRAM free/total: {free_gb:.2f}GB / {total_gb:.2f}GB")
        if free_gb < 5.5:
            print("[SD] UYARI: Bos VRAM dusuk. SD icin LM Studio gibi GPU uygulamalarini kapat.")
        if free_gb < 6.0:
            use_offload = True
            print("[SD] low-vram modu: model cpu offload aktif.")
            pipe.enable_model_cpu_offload()
        else:
            pipe.to(device)
    else:
        pipe.to(device)
    if device == "cuda":
        # 8GB VRAM sinifinda OOM azaltma
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        pipe.enable_vae_tiling()
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    pipe.set_progress_bar_config(disable=False)

    gen_device = "cuda" if device == "cuda" else "cpu"
    gen = torch.Generator(device=gen_device).manual_seed(args.seed)

    t0 = time.time()
    size_attempts = [
        (args.width, args.height),
        (640, 360),
        (512, 288),
    ]
    seen = set()
    size_attempts = [s for s in size_attempts if not (s in seen or seen.add(s))]
    result = None
    for w, h in size_attempts:
        try:
            print(f"[SD] deneme: {w}x{h}")
            result = pipe(
                prompt=args.prompt,
                negative_prompt=args.negative,
                num_inference_steps=args.steps,
                guidance_scale=args.cfg,
                width=w,
                height=h,
                generator=gen,
            )
            break
        except torch.OutOfMemoryError:
            print(f"[SD] OOM: {w}x{h} basarisiz, daha dusuk boyut deneniyor...")
            if device == "cuda":
                torch.cuda.empty_cache()
            continue
    if result is None:
        raise RuntimeError("SD OOM: tum boyut denemeleri basarisiz.")
    image = result.images[0]
    dt = time.time() - t0

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    print(f"[SD] kaydedildi: {out_path}")
    print(f"[SD] sure: {dt:.2f}s")

    if args.open_window:
        try:
            subprocess.Popen(["xdg-open", str(out_path)])
            print("[SD] pencere acildi (xdg-open).")
        except Exception as e:
            print(f"[SD] pencere acilamadi: {e}")


if __name__ == "__main__":
    main()
