#!/usr/bin/env python3
"""Validate the generated prode HTML before deploy."""

from __future__ import annotations

import sys
import json
from pathlib import Path

from prode_core import (
    SOURCE_KEYS,
    extract_key_values,
    extract_raw_match_objects,
    load_matches,
    validate_matches,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
PREDICTIONS_PATH = PROJECT_ROOT / "data" / "model" / "latest_predictions.json"


def validate() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    errors: list[str] = []

    checks = [
        ("<!DOCTYPE html>", "DOCTYPE missing"),
        ("<html", "HTML tag missing"),
        ("</html>", "HTML closing tag missing"),
        ("<script", "Script tag missing"),
        ("const matches = [", "Matches data missing"),
        ("function getConsensus", "getConsensus missing"),
        ("Chart.js", "Chart.js missing"),
        ("tab-dashboard", "Dashboard tab missing"),
        ("tab-noticias", "Noticias tab missing"),
    ]

    html_lower = html.lower()
    for check, message in checks:
        if check.lower() not in html_lower:
            errors.append(message)

    raw_matches = extract_raw_match_objects(html)
    for index, raw_match in enumerate(raw_matches, start=1):
        keys = [key for key, _ in extract_key_values(raw_match)]
        duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
        if duplicate_keys:
            errors.append(f"Match object {index} has duplicate keys: {', '.join(duplicate_keys)}")

    matches = load_matches(HTML_PATH)
    errors.extend(validate_matches(matches))

    expected_sources = len(SOURCE_KEYS)
    if f"Comparativa {expected_sources} IA" not in html:
        errors.append(f"Comparativa tab must show {expected_sources} IA")
    if f'id="stat-sources">{expected_sources}</div>' not in html:
        errors.append(f"Dashboard source count must be {expected_sources}")
    if "${x.cup}" not in html or "${x.pm}" not in html:
        errors.append("Comparative renderer must include Cup26 and Polymarket source cells")
    if "x.t</span>" in html or "m.t:" in html:
        errors.append("1960Tips must use the tips key; t caused a time-field collision")
    if "function renderDynamicTop3" not in html:
        errors.append("Dynamic top-3 renderer missing")
    if "const DYNAMIC_PREDICTIONS=" not in html:
        errors.append("Dynamic predictions JSON block missing")
    if "tab-dinamico" not in html:
        errors.append("Dynamic top-3 tab missing")

    if not PREDICTIONS_PATH.exists():
        errors.append("Latest predictions artifact missing")
    else:
        try:
            predictions = json.loads(PREDICTIONS_PATH.read_text(encoding="utf-8"))
            prediction_matches = predictions.get("matches", [])
            if len(prediction_matches) != 72:
                errors.append(f"Expected 72 dynamic predictions, found {len(prediction_matches)}")
            for item in prediction_matches:
                top_scores = item.get("top_scores", [])
                if len(top_scores) != 3:
                    errors.append(f"Match {item.get('id')} must have exactly 3 top scorelines")
                    continue
                probabilities = [score.get("probability") for score in top_scores]
                if any(not isinstance(probability, (int, float)) for probability in probabilities):
                    errors.append(f"Match {item.get('id')} has non-numeric probabilities")
                if probabilities != sorted(probabilities, reverse=True):
                    errors.append(f"Match {item.get('id')} top score probabilities are not sorted")
                if "motivation" not in item or "standings_snapshot" not in item:
                    errors.append(f"Match {item.get('id')} missing dynamic context fields")
            metadata = predictions.get("metadata", {})
            if metadata.get("dynamic_context") != "group_standings_and_round_motivation":
                errors.append("Dynamic predictions metadata missing standings/motivation context")
        except json.JSONDecodeError as exc:
            errors.append(f"Latest predictions JSON is invalid: {exc}")

    if errors:
        print("VALIDATION FAIL:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("VALIDATION OK: HTML structure correct")
    print(f"  - File size: {len(html)} bytes")
    print(f"  - Matches: {len(matches)}")
    print(f"  - Sources per match: {expected_sources}")
    print("  - Dynamic predictions: 72 matches with top 3")
    print("  - All required components present")


if __name__ == "__main__":
    validate()
