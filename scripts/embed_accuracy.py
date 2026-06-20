#!/usr/bin/env python3
"""
Embed accuracy data into the HTML dashboard.
Reads data/reports/accuracy_latest.json and injects
it between /* BEGIN_ACCURACY_DATA */ and /* END_ACCURACY_DATA */.
Also computes accuracy for external sources (ol, en, dk) from the HTML matches.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
ACCURACY_PATH = PROJECT_ROOT / "data" / "reports" / "accuracy_latest.json"
WEIGHTS_PATH = PROJECT_ROOT / "data" / "model" / "weights_latest.json"


def _extract_js_var(html: str, var_name: str) -> dict | list | None:
    m = re.search(rf"const\s+{var_name}\s*=\s*(\[.*?\]|\{{.*?\}})\s*;", html, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


def _evaluate(real: str, pred: str) -> str:
    """Return 'exact', 'winner', or 'wrong'."""
    if not pred or pred == "-" or not real:
        return "wrong"
    parts = pred.replace(" ", "").split("-")
    real_parts = real.replace(" ", "").split("-")
    if len(parts) != 2 or len(real_parts) != 2:
        return "wrong"
    try:
        pg, pv = int(parts[0]), int(parts[1])
        rg, rv = int(real_parts[0]), int(real_parts[1])
    except ValueError:
        return "wrong"
    if pg == rg and pv == rv:
        return "exact"
    if (pg > pv and rg > rv) or (pg < pv and rg < rv) or (pg == pv and rg == rv):
        return "winner"
    return "wrong"


def _parse_matches(html: str) -> list[dict]:
    """Extract matches array and external source dicts from HTML."""
    matches = _extract_js_var(html, "matches") or []
    real_scores = _extract_js_var(html, "EMBEDDED_REAL_SCORES") or {}
    olo = _extract_js_var(html, "OLORACULO_PREDS") or {}
    eng = _extract_js_var(html, "ENGINE_PREDS") or {}
    dk = _extract_js_var(html, "DK_PREDS") or {}
    return matches, real_scores, olo, eng, dk


def _compute_external_accuracy(matches, real_scores, external: dict[str, dict], label: str, weight: float):
    """Compute accuracy for an external source (ol, en, dk)."""
    exact = winner = wrong = 0
    total = 0
    for mid_str, pred in external.items():
        mid = int(mid_str)
        real = real_scores.get(mid_str) or real_scores.get(mid)
        if not real:
            continue
        total += 1
        e = _evaluate(real, pred)
        if e == "exact":
            exact += 1
            winner += 1
        elif e == "winner":
            winner += 1
        else:
            wrong += 1
    ea = round(exact / total * 100, 1) if total else 0
    wa = round(winner / total * 100, 1) if total else 0
    combined = round((ea * 0.3 + wa * 0.7), 1) if total else 0
    return {
        "label": label,
        "exact_accuracy": ea,
        "winner_accuracy": wa,
        "confidence_index": combined,
        "confidence_weighted": combined,
        "samples": total,
        "exact_hits": exact,
        "winner_hits": winner,
        "wrong": wrong,
        "current_weight": weight,
    }


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

    # Compute accuracy for external sources (ol, en, dk) from HTML data
    html = HTML_PATH.read_text(encoding="utf-8")
    matches, real_scores, olo, eng, dk = _parse_matches(html)
    external_sources = {
        "ol": (olo, "Oloráculo", 1.02),
        "en": (eng, "Engine", 1.13),
        "dk": (dk, "DraftKings", 2.5),
    }
    for key, (data, label, w) in external_sources.items():
        if key not in accuracy.get("sources", {}):
            accuracy.setdefault("sources", {})[key] = _compute_external_accuracy(
                matches, real_scores, data, label, w
            )

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
