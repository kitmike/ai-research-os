#!/usr/bin/env python3
"""Deterministic checks for AI Research OS static site."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "index.html",
    "README.md",
    "STYLE_GUIDE.md",
    "data/research.json",
    "data/agilentic_articles.json",
    ".github/workflows/pages.yml",
]
HTML_SENTINELS = [
    "AI Research OS",
    "Briefings & Essays",
    "Research Ledger",
    "Concept Dashboard",
    "data/research.json",
    "agilentic/ai-research-wire",
]


def main() -> int:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        print(f"missing required files: {missing}", file=sys.stderr)
        return 1

    data_path = ROOT / "data/research.json"
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"invalid JSON in {data_path}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, list):
        print("data/research.json must be a JSON array", file=sys.stderr)
        return 1

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    absent = [needle for needle in HTML_SENTINELS if needle not in html]
    if absent:
        print(f"index.html missing sentinels: {absent}", file=sys.stderr)
        return 1

    print("AI Research OS verification OK")
    print(f"records={len(data)} root={ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
