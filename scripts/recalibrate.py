#!/usr/bin/env python3
"""
Recalibrar pesos del consenso basado en accuracy historica.
Incluye:
- sample_factor progresivo (full confidence en 5 muestras)
- Ajuste agresivo de pesos (ci >= 20 → +0.15, ci <= 5 → -0.10)
- Bias tracking por fuente (sobrestima/infrasubestima goles)
- Time decay (resultados recientes pesan mas)
"""

from __future__ import annotations

import json
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from prode_core import SOURCE_KEYS, _DEFAULT_WEIGHTS, WEIGHTS_PATH, load_matches, parse_score, outcome

RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"
MODEL_DIR = PROJECT_ROOT / "data" / "model"
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
REPORT_DIR = PROJECT_ROOT / "data" / "reports"
BIAS_PATH = PROJECT_ROOT / "data" / "model" / "source_bias.json"

SOURCE_LABELS = {
    "c": "Cascade", "g": "ChatGPT", "f": "Gemini",
    "fs": "Fansided", "esp": "ESPN", "yh": "Yahoo",
    "tips": "1960Tips", "e": "ELO", "cup": "Cup26", "pm": "Polymarket",
}

RESULTS_LIST_PATH = PROJECT_ROOT / "data" / "runtime" / "results_order.json"
LATEST_PREDICTIONS_PATH = PROJECT_ROOT / "data" / "model" / "latest_predictions.json"
DRAW_INFLATION_PATH = PROJECT_ROOT / "data" / "model" / "draw_inflation.json"


def load_runtime(path: Path) -> dict:
    if not path.exists():
        return {"results": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def get_all_predictions(matches) -> dict[int, dict[str, str]]:
    preds = {}
    for match in matches:
        if match.id <= 72:
            preds[match.id] = dict(match.predictions)
    return preds


def load_results_order() -> list[str]:
    """Load chronological order of results for time decay."""
    if RESULTS_LIST_PATH.exists():
        return json.loads(RESULTS_LIST_PATH.read_text(encoding="utf-8"))
    return []


def save_results_order(order: list[str]) -> None:
    RESULTS_LIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_LIST_PATH.write_text(json.dumps(order, indent=2) + "\n", encoding="utf-8")


def time_decay_weights(results: dict[str, str], order: list[str]) -> dict[str, float]:
    """Assign higher weight to more recent results.
    Most recent result gets weight 1.0, oldest gets 0.5.
    Linear decay across the sequence.
    """
    if len(order) <= 1:
        return {mid: 1.0 for mid in results}

    decay = {}
    for i, mid in enumerate(order):
        if mid in results:
            decay[mid] = 0.5 + 0.5 * (i / (len(order) - 1))
    return decay


def calculate_source_accuracy(
    predictions: dict[int, dict[str, str]],
    results: dict[str, str],
) -> tuple[dict[str, dict], int, dict[str, dict]]:
    matched = 0
    source_data: dict[str, dict] = {
        k: {"exact": 0, "winner": 0, "total": 0, "samples": 0,
            "exact_weighted": 0.0, "winner_weighted": 0.0, "total_weighted": 0.0}
        for k in SOURCE_KEYS
    }
    bias_data: dict[str, dict] = {
        k: {"goal_diff_home": 0.0, "goal_diff_away": 0.0, "draw_predicted": 0,
            "draw_actual": 0, "count": 0}
        for k in SOURCE_KEYS
    }

    order = load_results_order()
    decay = time_decay_weights(results, order)

    for match_id_str, actual_score in results.items():
        match_id = int(match_id_str)
        pred = predictions.get(match_id)
        if not pred:
            continue

        w = decay.get(match_id_str, 1.0)
        actual_winner = outcome(actual_score)
        actual_home, actual_away = parse_score(actual_score)

        for source_key in SOURCE_KEYS:
            predicted_score = pred.get(source_key)
            if not predicted_score:
                continue

            source_data[source_key]["total"] += 1
            source_data[source_key]["samples"] += 1
            source_data[source_key]["total_weighted"] += w

            pred_home, pred_away = parse_score(predicted_score)
            bias_data[source_key]["goal_diff_home"] += pred_home - actual_home
            bias_data[source_key]["goal_diff_away"] += pred_away - actual_away
            bias_data[source_key]["count"] += 1
            if pred_home == pred_away:
                bias_data[source_key]["draw_predicted"] += 1
            if actual_home == actual_away:
                bias_data[source_key]["draw_actual"] += 1

            if predicted_score == actual_score:
                source_data[source_key]["exact"] += 1
                source_data[source_key]["winner"] += 1
                source_data[source_key]["exact_weighted"] += w
                source_data[source_key]["winner_weighted"] += w
            elif outcome(predicted_score) == actual_winner:
                source_data[source_key]["winner"] += 1
                source_data[source_key]["winner_weighted"] += w

    return source_data, matched, bias_data


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

        sample_factor = min(1.0, total / 5)
        confidence_index = round((0.3 * exact_acc + 0.7 * winner_acc) * sample_factor, 1)

        tw = sd["total_weighted"]
        exact_weighted_pct = (sd["exact_weighted"] / tw * 100) if tw > 0 else 0.0
        winner_weighted_pct = (sd["winner_weighted"] / tw * 100) if tw > 0 else 0.0
        confidence_weighted = round((0.3 * exact_weighted_pct + 0.7 * winner_weighted_pct) * sample_factor, 1)

        report[key] = {
            "label": SOURCE_LABELS.get(key, key),
            "exact_accuracy": round(exact_acc, 1),
            "winner_accuracy": round(winner_acc, 1),
            "confidence_index": confidence_index,
            "confidence_weighted": confidence_weighted,
            "samples": total,
            "exact_hits": sd["exact"],
            "winner_hits": sd["winner"],
            "current_weight": current_weights.get(key, 1.0),
        }
    return report


def build_bias_report(
    bias_data: dict[str, dict],
) -> dict[str, dict]:
    report = {}
    for key in SOURCE_KEYS:
        bd = bias_data[key]
        count = bd["count"]
        if count == 0:
            report[key] = {"goal_bias_home": 0.0, "goal_bias_away": 0.0,
                           "draw_frequency": 0.0, "actual_draw_frequency": 0.0, "samples": 0}
            continue
        report[key] = {
            "goal_bias_home": round(bd["goal_diff_home"] / count, 2),
            "goal_bias_away": round(bd["goal_diff_away"] / count, 2),
            "draw_frequency": round(bd["draw_predicted"] / count * 100, 1),
            "actual_draw_frequency": round(bd["draw_actual"] / count * 100, 1),
            "samples": count,
        }
    return report


def adjust_weights(
    report: dict[str, dict],
    current_weights: dict[str, float],
    bias_report: dict[str, dict],
) -> dict[str, float]:
    new_weights = {}

    for key in SOURCE_KEYS:
        r = report[key]
        weight = current_weights.get(key, 1.0)
        ci = r.get("confidence_weighted", r["confidence_index"])
        samples = r["samples"]

        if samples == 0:
            new_weights[key] = weight
            continue

        bias = bias_report.get(key, {})
        goal_bias = abs(bias.get("goal_bias_home", 0)) + abs(bias.get("goal_bias_away", 0))

        # Absolute CI-based adjustment (not relative to mean).
        # CI is a 0-100 score combining exact + winner accuracy.
        # CI >= 50 = strong, CI < 30 = weak.
        adj = 0.0
        if samples >= 3:
            raw_adj = (ci - 40.0) / 100.0
            # Decay the adjustment for small samples
            lr = min(1.0, samples / 10.0)
            adj = raw_adj * lr
            weight = round(weight + adj, 2)

        # Draw penalty: sources that severely under-predict draws lose weight
        actual_draw_rate = bias.get("actual_draw_frequency", 0)
        pred_draw_rate = bias.get("draw_frequency", 0)
        if samples >= 5 and abs(actual_draw_rate - pred_draw_rate) > 0.20:
            weight = max(0.3, round(weight - 0.10, 2))

        # Goal bias penalty
        if goal_bias > 1.0:
            weight = max(0.2, round(weight - 0.10 * min(1.0, goal_bias / 2.0), 2))

        weight = min(2.5, max(0.2, weight))
        new_weights[key] = weight

    # Normalize to prevent all weights hitting the upper cap.
    # Scale so the maximum weight is at 2.0, preserving relative ordering.
    max_w = max(new_weights.values())
    if max_w > 2.0:
        scale = 2.0 / max_w
        for k in new_weights:
            new_weights[k] = round(max(0.2, new_weights[k] * scale), 2)

    return new_weights


def save_weights(weights: dict, accuracies: dict, biases: dict, timestamp: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "weights": weights,
        "accuracies": accuracies,
        "biases": biases,
        "timestamp": timestamp,
        "generated_by": "recalibrate.py",
    }

    latest = MODEL_DIR / "weights_latest.json"
    latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    versioned = MODEL_DIR / f"weights_{timestamp}.json"
    versioned.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return latest


def save_bias(biases: dict, timestamp: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / f"bias_{timestamp}.json"
    path.write_text(json.dumps(biases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    latest = BIAS_PATH
    latest.write_text(json.dumps(biases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def save_report(report: dict, timestamp: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"accuracy_{timestamp}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    latest = REPORT_DIR / "accuracy_latest.json"
    latest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    print("=== Recalibrando Pesos (v2 — Bias + Time Decay) ===")

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

    source_data, matched, bias_data = calculate_source_accuracy(predictions, results)
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
    bias_report = build_bias_report(bias_data)

    print(f"\n  Partidos con resultado: {len(results)}")
    print(f"  Fuentes evaluadas: {len(SOURCE_KEYS)}")
    print()
    print(f"  {'Fuente':<20s} {'Exacta':>7s} {'Ganador':>8s} {'Confianza':>9s} {'Sesgo gol':>10s} {'Muestras':>8s} {'Peso':>6s}")
    print(f"  {'-'*71}")
    for key in SOURCE_KEYS:
        r = report[key]
        b = bias_report[key]
        gb = f"{b['goal_bias_home']:+.1f}/{b['goal_bias_away']:+.1f}"
        print(f"  {r['label']:<20s} {r['exact_accuracy']:>6.1f}% {r['winner_accuracy']:>7.1f}% "
              f"{r['confidence_index']:>8.1f}  {gb:>10s} {r['samples']:>4d}/{len(results):<3d} {r['current_weight']:>5.2f}")

    new_weights = adjust_weights(report, current_weights, bias_report)

    print(f"\n  Ajuste de pesos:")
    has_changes = False
    for key in SOURCE_KEYS:
        old_w = current_weights.get(key, 1.0)
        new_w = new_weights[key]
        if abs(new_w - old_w) > 0.01:
            diff = new_w - old_w
            reason = ""
            b = bias_report[key]
            if abs(b.get("goal_bias_home", 0)) + abs(b.get("goal_bias_away", 0)) > 1.0:
                reason = " (sesgo severo)"
            print(f"    {report[key]['label']:<20s} {old_w:.2f} -> {new_w:.2f} ({diff:+.2f}){reason}")
            has_changes = True
    if not has_changes:
        print("    (sin cambios significativos)")

    print(f"\n  Sesgo por fuente (gol local/visitante):")
    for key in SOURCE_KEYS:
        b = bias_report[key]
        if b["samples"] > 0:
            print(f"    {report[key]['label']:<20s}  local={b['goal_bias_home']:+.2f}  "
                  f"visit={b['goal_bias_away']:+.2f}  "
                  f"draw_pred={b['draw_frequency']:.0f}%  draw_real={b['actual_draw_frequency']:.0f}%")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    save_weights(new_weights, report, bias_report, timestamp)
    save_bias(bias_report, timestamp)
    save_report({
        "timestamp": timestamp,
        "matches_analyzed": len(results),
        "sources": report,
        "biases": bias_report,
        "weights_before": current_weights,
        "weights_after": new_weights,
    }, timestamp)

    print(f"\n  Pesos guardados: data/model/weights_latest.json")
    print(f"  Bias guardados: data/model/source_bias.json")
    print("  Recalibracion v2: OK")

    # --- Draw inflation calibration ---
    calibrate_draw_inflation(results, timestamp)


def calibrate_draw_inflation(results: dict[str, str], timestamp: str) -> None:
    """Calibrate draw_inflation base by comparing predicted vs actual draw rates."""
    print("\n=== Calibrando Draw Inflation ===")

    if not LATEST_PREDICTIONS_PATH.exists():
        print("  No hay latest_predictions.json. Se salta calibracion.")
        return

    model_data = json.loads(LATEST_PREDICTIONS_PATH.read_text(encoding="utf-8"))
    model_matches = {m["id"]: m for m in model_data.get("matches", [])}
    current_base = model_data.get("metadata", {}).get("draw_inflation_base", 0.55)

    predicted_draws: list[float] = []
    actual_draws: list[int] = []

    for match_id_str, actual_score in results.items():
        mid = int(match_id_str)
        mm = model_matches.get(mid)
        if not mm:
            continue
        draw_pct = mm.get("one_x_two", {}).get("draw")
        if draw_pct is None:
            continue
        h, a = parse_score(actual_score)
        predicted_draws.append(draw_pct / 100.0)
        actual_draws.append(1 if h == a else 0)

    if len(predicted_draws) < 3:
        print(f"  Solo {len(predicted_draws)} partidos con datos. Minimo 3.")
        return

    actual_rate = sum(actual_draws) / len(actual_draws)
    mean_predicted = sum(predicted_draws) / len(predicted_draws)
    brier_current = sum((p - o) ** 2 for p, o in zip(predicted_draws, actual_draws)) / len(predicted_draws)

    print(f"  Partidos: {len(predicted_draws)} | Draws reales: {sum(actual_draws)}/{len(actual_draws)} ({actual_rate*100:.1f}%)")
    print(f"  Draw predicho promedio: {mean_predicted*100:.1f}% | Base actual: {current_base:.2f} | Brier: {brier_current:.4f}")

    best_base = current_base
    best_brier = brier_current
    candidates = [round(0.30 + i * 0.10, 2) for i in range(18)]

    for candidate in candidates:
        adjusted = [min(0.95, max(0.01, p * candidate / max(current_base, 0.01))) for p in predicted_draws]
        brier = sum((a - o) ** 2 for a, o in zip(adjusted, actual_draws)) / len(adjusted)
        if brier < best_brier:
            best_brier = brier
            best_base = candidate

    learning_rate = min(1.0, len(predicted_draws) / 15.0)
    smoothed_base = round(max(0.30, min(2.00, current_base + (best_base - current_base) * learning_rate)), 2)

    payload = {
        "base_inflation": smoothed_base,
        "current_base_used": current_base,
        "grid_best_base": best_base,
        "brier_before": round(brier_current, 4),
        "brier_after": round(best_brier, 4),
        "draws_analyzed": len(predicted_draws),
        "actual_draw_rate": round(actual_rate, 4),
        "mean_predicted_draw_rate": round(mean_predicted, 4),
        "learning_rate": round(learning_rate, 2),
        "timestamp": timestamp,
    }
    DRAW_INFLATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRAW_INFLATION_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"  Mejor base: {best_base:.2f} (Brier: {best_brier:.4f})")
    print(f"  Base suavizada (lr={learning_rate:.2f}): {smoothed_base:.2f}")
    print(f"  Guardado: {DRAW_INFLATION_PATH}")


if __name__ == "__main__":
    main()
