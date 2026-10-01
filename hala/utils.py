"""أدوات مشتركة للمشروع"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_json(name: str) -> dict:
    """يحمّل ملف JSON من مجلد data."""
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)
