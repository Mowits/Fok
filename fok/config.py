import json
import os


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_db_path(config_path: str, cfg: dict) -> str:
    base = os.path.dirname(config_path)
    db_path = cfg.get("db_path", "fok_memory.db")
    if os.path.isabs(db_path):
        return db_path
    return os.path.join(base, db_path)
