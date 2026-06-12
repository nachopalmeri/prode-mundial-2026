#!/usr/bin/env python3
"""
Embed accuracy data into the HTML dashboard.
Reads data/reports/accuracy_latest.json and injects
it between /* BEGIN_ACCURACY_DATA */ and /* END_ACCURACY_DATA */.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
ACCURACY_PATH = PROJECT_ROOT / "data" / "reports" / "accuracy_latest.json"
WEIGHTS_PATH = PROJECT_ROOT / "data" / "model" / "weights_latest.json"


def main() -> None:
    print("=== Embedding Accuracy Data ===")

    if not ACCURACY_PATH.exists():
        print("  No accuracy data found. Run recalibrate.py first.")
        return

    accuracy = json.loads(ACCURACY_PATH.read_text(encoding="utf-8"))
    weights = {}
    if WEIGHTS_PATH.exists():
        try:
            wdata = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
            weights = wdata.get("weights", wdata)
        except json.JSONDecodeError:
            pass

    for key, src in accuracy.get("sources", {}).items():
        if isinstance(src, dict):
            src["current_weight"] = float(weights.get(key, 1.0))

    sources = accuracy.get("sources", {})
    active = [s for s in sources.values() if isinstance(s, dict) and s.get("samples", 0) > 0]
    if active:
        global_exact = sum(s["exact_hits"] for s in active) / sum(s["samples"] for s in active) * 100
        global_winner = sum(s["winner_hits"] for s in active) / sum(s["samples"] for s in active) * 100
    else:
        global_exact = global_winner = 0.0
    accuracy["global_winrate"] = {
        "exact_accuracy": round(global_exact, 1),
        "winner_accuracy": round(global_winner, 1),
    }

    embed_data = json.dumps(accuracy, ensure_ascii=False)

    html = HTML_PATH.read_text(encoding="utf-8")
    pattern = r"/\* BEGIN_ACCURACY_DATA \*/[^/]*/\* END_ACCURACY_DATA \*/"
    replacement = f"/* BEGIN_ACCURACY_DATA */\nconst ACCURACY_DATA = {embed_data};\n/* END_ACCURACY_DATA */"

    if not re.search(pattern, html):
        print("  ERROR: BEGIN_ACCURACY_DATA / END_ACCURACY_DATA markers not found in HTML")
        return

    new_html = re.sub(pattern, replacement, html)
    HTML_PATH.write_text(new_html, encoding="utf-8")
    print(f"  Accuracy data embedded ({len(accuracy.get('sources', {}))} sources)")


if __name__ == "__main__":
    main()
