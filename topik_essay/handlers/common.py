# handlers/common.py
import json
from pathlib import Path
from datetime import datetime

# Configure admin id (replace with your Telegram ID)
ADMIN_ID = 691728393

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "essays.json"
LOG_FILE = DATA_DIR / "user_activity.json"

def _read_json_safe(path: Path):
    """
    Return parsed JSON from path. If file missing/empty/corrupt, return empty dict.
    """
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8").strip()
        if text == "":
            return {}
        return json.loads(text)
    except (json.JSONDecodeError, OSError) as e:
        # If file corrupted, back it up and return empty dict
        backup = path.with_suffix(path.suffix + ".bak")
        try:
            path.replace(backup)
        except Exception:
            # best-effort; ignore if backup fails
            pass
        return {}

def _write_json_safe(path: Path, data):
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        # Could log to file; for now, print for debugging
        print(f"[handlers.common] Failed to write {path}: {e}")
        return False

def save_essay(user_id: int, essay_text: str, score: int = None):
    """
    Save or update essay for a user. Works even if file was empty or corrupted.
    """
    data = _read_json_safe(DATA_FILE)
    uid = str(user_id)
    entry = {
        "text": essay_text,
        "score": score,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    # Append to history list per user for audit
    if uid not in data:
        data[uid] = {"history": [entry]}
    else:
        # keep history array to preserve all submissions
        if "history" not in data[uid]:
            data[uid]["history"] = []
        data[uid]["history"].append(entry)
    _write_json_safe(DATA_FILE, data)
    return True

def load_all_essays():
    return _read_json_safe(DATA_FILE)

def log_user_activity(user, command: str):
    """
    user: telegram.User object
    command: string, e.g. "/essay"
    """
    log = _read_json_safe(LOG_FILE)
    uid = str(user.id)
    info = log.get(uid, {})
    if not info:
        info = {
            "name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
            "username": getattr(user, "username", "") or "",
            "first_seen": datetime.utcnow().isoformat() + "Z",
            "commands": []
        }
    info["last_seen"] = datetime.utcnow().isoformat() + "Z"
    info.setdefault("commands", []).append({"command": command, "ts": datetime.utcnow().isoformat() + "Z"})
    log[uid] = info
    _write_json_safe(LOG_FILE, log)

def count_squares(text: str) -> int:
    """
    Heuristic: count characters as squares. You can replace with tokenization rules later.
    """
    if not text:
        return 0
    return len(text)
