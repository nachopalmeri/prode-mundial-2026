#!/usr/bin/env python3
"""Export current source consensus as an external-predictions baseline."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from prode_core import consensus_score, load_matches


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def build_output(timestamp: str) -> dict:
    matches = load_matches()
    seed_predictions = {str(match.id): consensus_score(match.predictions).replace(" ", "") for match in matches}
    output = {
        "timestamp": timestamp,
        "status": "baseline",
        "seed_predictions": seed_predictions,
        "match_count": len(seed_predictions),
        "note": "Baseline derived from the current fixture-aware 10-source consensus.",
    }
    (RAW / f"external_preds_{timestamp}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"External baseline saved: external_preds_{timestamp}.json | matches={len(seed_predictions)}")
    return output


def main() -> None:
    build_output(datetime.now().strftime("%Y%m%d_%H%M"))


if __name__ == "__main__":
    main()
