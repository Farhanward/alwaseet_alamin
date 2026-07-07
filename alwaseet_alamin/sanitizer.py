from __future__ import annotations

import hashlib
import re


PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[EMAIL]"),
    ("SA_PHONE", re.compile(r"(?<!\d)(?:\+?966|0)?5\d{8}(?!\d)"), "[PHONE]"),
    ("API_KEY", re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{12,})['\"]?"), "[SECRET]"),
    ("OPENAI_KEY", re.compile(r"sk-[A-Za-z0-9]{20,}"), "[OPENAI_KEY]"),
    ("PAYMENT_KEY", re.compile(r"\b[sp]k_(?:live|test)_[A-Za-z0-9]{8,}\b"), "[PAYMENT_KEY]"),
    ("GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[GITHUB_TOKEN]"),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[SLACK_TOKEN]"),
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}"), "[AWS_ACCESS_KEY]"),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[PRIVATE_KEY]"),
]


def _finding(code: str, value: str, replacement: str) -> dict:
    return {
        "code": code,
        "evidence": replacement,
        "length": len(value),
        "fingerprint": hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:16],
    }


def sanitize(text: str) -> dict:
    sanitized = text
    findings = []
    for code, pattern, replacement in PATTERNS:
        for match in list(pattern.finditer(sanitized)):
            findings.append(_finding(code, match.group(0), replacement))
        sanitized = pattern.sub(replacement, sanitized)
    changed = sanitized != text
    return {"sanitized": sanitized, "changed": changed, "findings": findings}
