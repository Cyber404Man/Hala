"""أدوات مشتركة للمشروع"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
STATE_DIR = Path.home() / ".hala"
STATE_FILE = STATE_DIR / "sitr_state.json"


def load_json(name: str) -> dict:
    """يحمّل ملف JSON من مجلد data."""
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    """يحمّل حالة sitr (أي مواقع تم الحذف منها)."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        return {"completed": [], "notes": {}}
    with STATE_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """يحفظ حالة sitr."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def mark_completed(site_id: str) -> None:
    """يعلّم موقع كمكتمل."""
    state = load_state()
    if site_id not in state["completed"]:
        state["completed"].append(site_id)
    save_state(state)


def mark_pending(site_id: str) -> None:
    """يشيل موقع من المكتمل."""
    state = load_state()
    if site_id in state["completed"]:
        state["completed"].remove(site_id)
    save_state(state)


def reset_state() -> None:
    """يصفّر كل الحالة."""
    save_state({"completed": [], "notes": {}})
