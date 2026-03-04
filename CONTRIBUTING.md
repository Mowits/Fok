# Contributing

Thanks for contributing to FOK Modular.

## Development Setup

```bash
cd /home/mowits/Downloads/fok_modular
./install_pc.sh
```

Optional stacks:
- Whisper STT: `./install_pc_whisper.sh`
- Piper TTS: `./install_pc_piper.sh`
- Stable Diffusion: `./install_pc_sd.sh`

## Coding Guidelines

- Keep modules focused and small.
- Prefer explicit logs over silent failures.
- Keep backward compatibility for existing command aliases where possible.
- Do not commit secrets, API keys, or private SSH material.

## Validation

Before opening a PR:

```bash
python3 -m py_compile main.py fok/*.py
bash -n run_all_pc_pi.sh run_sd.sh
```

If you touched SD paths, also verify:

```bash
./run_all_pc_pi.sh sd "test prompt"
tail -n 50 /tmp/fok_sd.log
```

## Pull Requests

- Use clear commit messages.
- Explain behavior changes and tradeoffs.
- Include exact test commands and observed output.
