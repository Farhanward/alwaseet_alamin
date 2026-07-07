from __future__ import annotations

import json
import statistics
import time
import tracemalloc
from pathlib import Path

from .gate import decide


def convert_neuralchemy(events_path: str | Path, out_path: str | Path) -> dict:
    source = Path(events_path)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = unsafe = safe = 0
    with source.open("r", encoding="utf-8") as handle, out.open("w", encoding="utf-8") as output:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            event = rec.get("event") or {}
            text = str(event.get("content") or "")
            label = int(rec.get("label", 0))
            if rows % 23 == 0:
                text += " contact user@example.com token='sk-12345678901234567890'"
            output.write(json.dumps({"text": text, "expected_unsafe": bool(label), "label": label}, ensure_ascii=False) + "\n")
            rows += 1
            unsafe += 1 if label else 0
            safe += 0 if label else 1
    return {"source": str(source.resolve()), "out": str(out.resolve()), "rows": rows, "unsafe": unsafe, "safe": safe}


def _p(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, int(round((pct / 100) * (len(values) - 1))))]


def evaluate(path: str | Path, repeat: int = 1) -> dict:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    tp = tn = fp = fn = errors = leaks = 0
    lat = []
    start = time.perf_counter()
    tracemalloc.start()
    for _ in range(repeat):
        for row in rows:
            expected = bool(row.get("expected_unsafe"))
            t0 = time.perf_counter()
            try:
                result = decide(str(row.get("text") or ""))
                predicted = result["action"] in {"BLOCK", "QUARANTINE"}
                result_blob = json.dumps(result, ensure_ascii=False)
                if "sk-" in result_blob or "user@example.com" in result_blob:
                    leaks += 1
            except Exception:
                errors += 1
                predicted = True
            lat.append((time.perf_counter() - t0) * 1000)
            if expected and predicted:
                tp += 1
            elif expected and not predicted:
                fn += 1
            elif not expected and predicted:
                fp += 1
            else:
                tn += 1
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    accuracy = (tp + tn) / max(1, tp + tn + fp + fn)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"input": str(Path(path).resolve()), "records": len(rows), "repeat": repeat, "processed": len(rows) * repeat, "errors": errors, "leaks": leaks, "metrics": {"accuracy": accuracy, "precision": precision, "recall": recall, "specificity": specificity, "f1": f1, "tp": tp, "tn": tn, "fp": fp, "fn": fn}, "latency_ms": {"mean": statistics.fmean(lat) if lat else 0.0, "p99": _p(lat, 99), "max": max(lat) if lat else 0.0}, "memory_mb": {"current": current / 1_000_000, "peak": peak / 1_000_000}, "elapsed_seconds": time.perf_counter() - start, "collapse_check": {"passed": errors == 0 and leaks == 0, "criteria": "errors == 0 and leaks == 0"}}
