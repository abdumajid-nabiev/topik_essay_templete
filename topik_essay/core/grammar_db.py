# core/grammar_db.py
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_PATH = Path("data/grammar.json")

SAMPLE = [
    {
        "pattern": "-(으)므로",
        "function": "Cause/Effect",
        "levels": ["5-6"],
        "meaning_en": "because / since (formal)",
        "meaning_uz": "chunki (formal)",
        "example_kr": "그는 아팠으므로 결석했습니다.",
        "frequency_rank": 120
    },
    {
        "pattern": "-(으)니까",
        "function": "Cause/Effect",
        "levels": ["3-4","5-6"],
        "meaning_en": "because / so",
        "meaning_uz": "chunki / shuning uchun",
        "example_kr": "비가 오니까 우산을 가져오세요.",
        "frequency_rank": 80
    },
    {
        "pattern": "-지만",
        "function": "Contrast/Concession",
        "levels": ["3-4","5-6"],
        "meaning_en": "but / however",
        "meaning_uz": "ammo",
        "example_kr": "좋아하지만 살 시간이 없다.",
        "frequency_rank": 60
    }
]

def load_all() -> List[Dict[str, Any]]:
    if DATA_PATH.exists():
        try:
            raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return raw
            if isinstance(raw, dict) and "entries" in raw:
                return raw["entries"]
        except Exception:
            pass
    return SAMPLE.copy()

GRAMMAR = load_all()

def list_functions() -> List[str]:
    return sorted({entry.get("function", "Other") for entry in GRAMMAR})

def list_levels() -> List[str]:
    return sorted({lvl for entry in GRAMMAR for lvl in entry.get("levels", [])})

def filter_entries(function: Optional[str]=None, level: Optional[str]=None, keyword: Optional[str]=None) -> List[Dict[str,Any]]:
    res = []
    for e in GRAMMAR:
        if function and e.get("function","") != function:
            continue
        if level:
            if level not in e.get("levels", []):
                continue
        if keyword:
            k = keyword.lower()
            if k not in e.get("pattern","").lower() and k not in e.get("example_kr","").lower():
                continue
        res.append(e)
    res.sort(key=lambda x: (x.get("frequency_rank", 9999), x.get("pattern","")))
    return res

def paginate(entries: List[Dict[str,Any]], page:int=1, per_page:int=5):
    total = len(entries)
    start = (page-1)*per_page
    end = start + per_page
    return entries[start:end], total
