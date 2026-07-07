from __future__ import annotations

import sys
from pathlib import Path

from .sanitizer import sanitize

_ALMUNAA_CACHE = None


def _load_almunaa():
    global _ALMUNAA_CACHE
    if _ALMUNAA_CACHE is not None:
        return _ALMUNAA_CACHE
    root = Path("C:/Projects/almunaa")
    if root.exists() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from almunaa.core import scan_event
        from almunaa.lexical_model import LexicalModel
        from almunaa.models import AgentEvent

        model = None
        model_path = root / "models" / "almunaa_lexical_guard.json"
        if model_path.exists():
            model = LexicalModel.load(model_path)
        _ALMUNAA_CACHE = (scan_event, AgentEvent, model)
        return _ALMUNAA_CACHE
    except Exception:
        _ALMUNAA_CACHE = (None, None, None)
        return _ALMUNAA_CACHE


def _should_use_model(text: str) -> bool:
    clean = text.strip()
    if len(clean) < 30:
        return False
    latin = sum(1 for char in clean.lower() if "a" <= char <= "z")
    return latin >= 12 and "[secret]" not in clean.lower()


def decide(text: str, user: str = "human") -> dict:
    clean = sanitize(text)
    scan_event, AgentEvent, model = _load_almunaa()
    immunity = {"action": "ALLOW", "score": 100, "findings": []}
    if scan_event and AgentEvent:
        event = AgentEvent.from_dict({"kind": "input", "agent": f"proxy:{user}", "content": clean["sanitized"], "context": {"proxy": "alwaseet_alamin"}})
        immunity = scan_event(event, write_ledger=False, write_quarantine=False, lexical_model=model if _should_use_model(clean["sanitized"]) else None).to_dict()
    action = immunity.get("action", "ALLOW")
    if clean["findings"] and action == "ALLOW":
        action = "REVIEW"
    if action in {"BLOCK", "QUARANTINE"}:
        outbound = ""
    else:
        outbound = clean["sanitized"]
    return {"action": action, "outbound": outbound, "sanitization": clean, "immunity": immunity}
