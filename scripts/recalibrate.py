#!/usr/bin/env python3
"""
Recalibrar pesos del consenso basado en accuracy historica.
Lee resultados reales de data/runtime/results.json.
Compara cada fuente vs el resultado real.
Calcula confidence_index por fuente.
Guarda weights_latest.json para que prode_core.py lo cargue.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from prode_core import SOURCE_KEYS, _DEFAULT_WEIGHTS, WEIGHTS_PATH, load_matches, parse_score, outcome

RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"
MODEL_DIR = PROJECT_ROOT / "data" / "model"
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
REPORT_DIR = PROJECT_ROOT / "data" / "reports"

SOURCE_LABELS = {
    "c": "Cup26", "g": "Gamble", "f": "Futbolist",
    "fs": "F Score", "esp": "ESPN", "yh": "Yahoo",
    "tips": "1960 Tips", "e": "Elo", "cup": "Cup Predictor", "pm": "Polymarket",
}


def load_runtime(path: Path) -> dict:
    if not path.exists():
        return {"results": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def get_all_predictions(matches) -> dict[int, dict[str, str]]:
    """Build {match_id: {source: score}} from HTML match data."""
    preds = {}
    for match in matches:
        if match.id <= 72:
            preds[match.id] = dict(match.predictions)
    return preds


def calculate_source_accuracy(
    predictions: dict[int, dict[str, str]],
    results: dict[str, str],
) -> dict[str, dict]:
    matched = 0
    source_data: dict[str, dict] = {
        k: {"exact": 0, "winner": 0, "total": 0, "samples": 0} for k in SOURCE_KEYS
    }

    for match_id_str, actual_score in results.items():
        match_id = int(match_id_str)
        pred = predictions.get(match_id)
        if not pred:
            continue

        actual_winner = outcome(actual_score)
        for source_key in SOURCE_KEYS:
            predicted_score = pred.get(source_key)
            if not predicted_score:
                continue
            source_data[source_key]["total"] += 1
            source_data[source_key]["samples"] += 1

            if predicted_score == actual_score:
                source_data[source_key]["exact"] += 1
                source_data[source_key]["winner"] += 1
            elif outcome(predicted_score) == actual_winner:
                source_data[source_key]["winner"] += 1

    return source_data, matched


def build_accuracy_report(
    source_data: dict[str, dict],
    current_weights: dict[str, float],
) -> dict:
    report = {}
    for key in SOURCE_KEYS:
        sd = source_data[key]
        total = sd["total"]
        if total == 0:
            report[key] = {
                "label": SOURCE_LABELS.get(key, key),
                "exact_accuracy": 0.0,
                "winner_accuracy": 0.0,
                "confidence_index": 0.0,
                "samples": 0,
                "current_weight": current_weights.get(key, 1.0),
                "new_weight": current_weights.get(key, 1.0),
            }
            continue

        exact_acc = sd["exact"] / total * 100
        winner_acc = sd["winner"] / total * 100

        sample_factor = min(1.0, total / 20)
        confidence_index = round((0.3 * exact_acc + 0.7 * winner_acc) * sample_factor, 1)

        report[key] = {
            "label": SOURCE_LABELS.get(key, key),
            "exact_accuracy": round(exact_acc, 1),
            "winner_accuracy": round(winner_acc, 1),
            "confidence_index": confidence_index,
            "samples": total,
            "exact_hits": sd["exact"],
            "winner_hits": sd["winner"],
            "current_weight": current_weights.get(key, 1.0),
        }
    return report


def adjust_weights(
    report: dict[str, dict],
    current_weights: dict[str, float],
) -> dict[str, float]:
    new_weights = {}
    for key in SOURCE_KEYS:
        r = report[key]
        weight = current_weights.get(key, 1.0)
        ci = r["confidence_index"]
        samples = r["samples"]

        if samples == 0:
            new_weights[key] = weight
            continue

        if ci >= 40:
            weight = min(2.0, round(weight + 0.20, 2))
        elif ci >= 25:
            weight = min(2.0, round(weight + 0.10, 2))
        elif ci >= 15:
            weight = round(weight + 0.02, 2)
        elif ci <= 5 and samples >= 5:
            weight = max(0.4, round(weight - 0.15, 2))
        elif ci <= 10 and samples >= 3:
            weight = max(0.4, round(weight - 0.05, 2))

        new_weights[key] = weight

    return new_weights


def save_weights(weights: dict, accuracies: dict, timestamp: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "weights": weights,
        "accuracies": accuracies,
        "timestamp": timestamp,
        "generated_by": "recalibrate.py",
    }

    latest = MODEL_DIR / "weights_latest.json"
    latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    versioned = MODEL_DIR / f"weights_{timestamp}.json"
    versioned.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return latest


def save_report(report: dict, timestamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"accuracy_{timestamp}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    latest = REPORT_DIR / "accuracy_latest.json"
    latest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    print("=== Recalibrando Pesos (Accuracy Tracking) ===")

    runtime = load_runtime(RUNTIME_PATH)
    results = runtime.get("results", {})

    if not results:
        print("  No hay resultados registrados. Ejecutar primero:")
        print("    python scripts/fetch_results.py")
        print("  Usando pesos default.")
        return

    html = HTML_PATH.read_text(encoding="utf-8")
    matches = load_matches(HTML_PATH)
    predictions = get_all_predictions(matches)

    source_data, _ = calculate_source_accuracy(predictions, results)
    current_weights = _DEFAULT_WEIGHTS
    weights_path = WEIGHTS_PATH
    if weights_path.exists():
        try:
            data = json.loads(weights_path.read_text(encoding="utf-8"))
            loaded = data.get("weights", data)
            current_weights = {k: float(v) for k, v in loaded.items() if k in SOURCE_KEYS}
        except (json.JSONDecodeError, ValueError):
            pass

    report = build_accuracy_report(source_data, current_weights)

    print(f"\n  Partidos con resultado: {len(results)}")
    print(f"  Fuentes evaluadas: {len(SOURCE_KEYS)}")
    print()
    print(f"  {'Fuente':<20s} {'Exacta':>7s} {'Ganador':>8s} {'Confianza':>9s} {'Muestras':>8s} {'Peso':>6s}")
    print(f"  {'-'*58}")
    for key in SOURCE_KEYS:
        r = report[key]
        print(f"  {r['label']:<20s} {r['exact_accuracy']:>6.1f}% {r['winner_accuracy']:>7.1f}% "
              f"{r['confidence_index']:>8.1f}  {r['samples']:>4d}/{len(results):<3d} {r['current_weight']:>5.2f}")

    new_weights = adjust_weights(report, current_weights)

    print(f"\n  Ajuste de pesos:")
    has_changes = False
    for key in SOURCE_KEYS:
        old_w = current_weights.get(key, 1.0)
        new_w = new_weights[key]
        if abs(new_w - old_w) > 0.01:
            diff = new_w - old_w
            print(f"    {report[key]['label']:<20s} {old_w:.2f} -> {new_w:.2f} ({diff:+.2f})")
            has_changes = True
    if not has_changes:
        print("    (sin cambios significativos)")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    save_weights(new_weights, report, timestamp)
    save_report({
        "timestamp": timestamp,
        "matches_analyzed": len(results),
        "sources": report,
        "weights_before": current_weights,
        "weights_after": new_weights,
    }, timestamp)

    print(f"\n  Pesos guardados: data/model/weights_latest.json")
    print("  Recalibracion: OK")


if __name__ == "__main__":
    main()
