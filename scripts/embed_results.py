#!/usr/bin/env python3
"""
Embed real match results into the HTML dashboard.
Reads data/runtime/results.json and injects as EMBEDDED_REAL_SCORES
so the dashboard scoreboard and comparativa tab reflect actual scores.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
RESULTS_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"


MARKER_BEGIN = "/* BEGIN_REAL_SCORES */"
MARKER_END = "/* END_REAL_SCORES */"


def main() -> None:
    print("=== Embedding Real Scores ===")

    if not RESULTS_PATH.exists():
        print("  No results.json found.")
        return

    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    results = data.get("results", {})

    if not results:
        print("  No results to embed.")
        return

    embed_data = json.dumps(results, ensure_ascii=False)
    replacement = f"{MARKER_BEGIN}\nconst EMBEDDED_REAL_SCORES = {embed_data};\n{MARKER_END}"

    html = HTML_PATH.read_text(encoding="utf-8")

    if MARKER_BEGIN in html:
        pattern = re.compile(rf"{re.escape(MARKER_BEGIN)}[^/]*{re.escape(MARKER_END)}")
        new_html = pattern.sub(replacement, html)
        print(f"  Updated existing markers ({len(results)} result(s))")
    else:
        new_html = html.replace(
            "/* BEGIN_ACCURACY_DATA */",
            f"{replacement}\n\n/* BEGIN_ACCURACY_DATA */",
        )
        print(f"  Added REAL_SCORES markers ({len(results)} result(s))")

    HTML_PATH.write_text(new_html, encoding="utf-8")
    print(f"  Embedded {len(results)} real score(s) into HTML")


if __name__ == "__main__":
    main()
