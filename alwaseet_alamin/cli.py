from __future__ import annotations

import argparse
import json
from pathlib import Path

from .batch import convert_neuralchemy, evaluate
from .gate import decide


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="alwaseet", description="الوسيط الآمن: تعقيم وحوكمة AI.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    san = sub.add_parser("gate")
    san.add_argument("--text", required=True)
    conv = sub.add_parser("convert-neuralchemy")
    conv.add_argument("--events", default="C:/Projects/almunaa/data/benchmarks/neuralchemy_prompt_injection_full.events.jsonl")
    conv.add_argument("--out", default="data/benchmarks/alwaseet_neuralchemy_proxy.jsonl")
    batch = sub.add_parser("batch")
    batch.add_argument("--input", required=True)
    batch.add_argument("--json-out", default="reports/alwaseet_benchmark.json")
    batch.add_argument("--report", default="reports/alwaseet_benchmark.md")
    stress = sub.add_parser("stress")
    stress.add_argument("--input", required=True)
    stress.add_argument("--repeat", type=int, default=3)
    stress.add_argument("--json-out", default="reports/alwaseet_stress.json")
    stress.add_argument("--report", default="reports/alwaseet_stress.md")
    serve = sub.add_parser("serve")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    sub.add_parser("version")
    args = parser.parse_args(argv)
    if args.cmd == "serve":
        from .service import run_server

        run_server(host=args.host, port=args.port)
        return 0
    if args.cmd == "version":
        from .version import __version__

        print(json.dumps({"service": "alwaseet-alamin", "version": __version__}, ensure_ascii=False))
        return 0
    if args.cmd == "gate":
        print(json.dumps(decide(args.text), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "convert-neuralchemy":
        print(json.dumps(convert_neuralchemy(args.events, args.out), ensure_ascii=False, indent=2))
        return 0
    if args.cmd in {"batch", "stress"}:
        summary = evaluate(args.input, repeat=getattr(args, "repeat", 1))
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        text = f"# تقرير الوسيط الآمن\n\n- processed: `{summary['processed']}`\n- errors: `{summary['errors']}`\n- leaks: `{summary['leaks']}`\n- F1: `{summary['metrics']['f1']:.4f}`\n- precision: `{summary['metrics']['precision']:.4f}`\n- recall: `{summary['metrics']['recall']:.4f}`\n- specificity: `{summary['metrics']['specificity']:.4f}`\n- p99: `{summary['latency_ms']['p99']:.4f}ms`\n- peak memory: `{summary['memory_mb']['peak']:.4f}MB`\n- collapse: `{'PASS' if summary['collapse_check']['passed'] else 'FAIL'}`\n"
        Path(args.report).write_text(text, encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if summary["collapse_check"]["passed"] else 2
    raise ValueError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
