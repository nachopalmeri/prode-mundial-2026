#!/usr/bin/env python3
"""
Validar predicciones vs resultados reales.
Genera reporte con accuracy por fuente, aciertos exactos,
aciertos de ganador, y recomendaciones.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from prode_core import SOURCE_KEYS, _DEFAULT_WEIGHTS, load_matches, parse_score, outcome, WEIGHTS_PATH

RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
REPORT_DIR = PROJECT_ROOT / "data" / "reports"

SOURCE_LABELS = {
    "c": "Cup26", "g": "Gamble", "f": "Futbolist",
    "fs": "F Score", "esp": "ESPN", "yh": "Yahoo",
    "tips": "1960 Tips", "e": "Elo", "cup": "Cup Predictor", "pm": "Polymarket",
}

SOURCE_NAMES_SHORT = {
    "c": "Cup26", "g": "Gmbl", "f": "Futb",
    "fs": "FScr", "esp": "ESPN", "yh": "Yhoo",
    "tips": "Tips", "e": "Elo", "cup": "CupP", "pm": "Poly",
}


def load_runtime(path: Path) -> dict:
    if not path.exists():
        return {"results": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def load_current_weights() -> dict[str, float]:
    if WEIGHTS_PATH.exists():
        try:
            data = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
            loaded = data.get("weights", data)
            return {k: float(v) for k, v in loaded.items() if k in SOURCE_KEYS}
        except (json.JSONDecodeError, ValueError):
            pass
    return dict(_DEFAULT_WEIGHTS)


def validate() -> dict | None:
    runtime = load_runtime(RUNTIME_PATH)
    results = runtime.get("results", {})

    if not results:
        print("  No hay resultados registrados aun.")
        print("  Usar: python scripts/fetch_results.py")
        return None

    matches = load_matches(HTML_PATH)
    weights = load_current_weights()

    report = {
        "validation_date": datetime.now(timezone.utc).isoformat(),
        "matches_evaluated": len(results),
        "total_matches": 72,
        "group_standings_updated": False,
        "sources": {},
        "overall": {},
        "consensus": {},
        "recommendations": [],
        "weights": weights,
    }

    total_sources = {k: {"exact": 0, "winner": 0, "total": 0} for k in SOURCE_KEYS}
    consensus_correct_exact = 0
    consensus_correct_winner = 0
    consensus_total = 0

    for match_id_str, actual_score in results.items():
        match_id = int(match_id_str)
        match = next((m for m in matches if m.id == match_id), None)
        if not match:
            continue

        actual_winner = outcome(actual_score)

        preds = match.predictions
        consensus = _compute_consensus(preds, weights)
        consensus_total += 1
        if consensus == actual_score:
            consensus_correct_exact += 1
            consensus_correct_winner += 1
        elif outcome(consensus) == actual_winner:
            consensus_correct_winner += 1

        for key in SOURCE_KEYS:
            pred = preds.get(key)
            if not pred:
                continue
            total_sources[key]["total"] += 1
            if pred == actual_score:
                total_sources[key]["exact"] += 1
                total_sources[key]["winner"] += 1
            elif outcome(pred) == actual_winner:
                total_sources[key]["winner"] += 1

    for key in SOURCE_KEYS:
        sd = total_sources[key]
        total = sd["total"]
        if total == 0:
            report["sources"][key] = {
                "label": SOURCE_LABELS.get(key, key),
                "exact_accuracy": 0, "winner_accuracy": 0,
                "exact_hits": 0, "winner_hits": 0, "total": 0,
            }
            continue
        report["sources"][key] = {
            "label": SOURCE_LABELS.get(key, key),
            "exact_accuracy": round(sd["exact"] / total * 100, 1),
            "winner_accuracy": round(sd["winner"] / total * 100, 1),
            "exact_hits": sd["exact"],
            "winner_hits": sd["winner"],
            "total": total,
        }

    if consensus_total > 0:
        report["consensus"] = {
            "exact_accuracy": round(consensus_correct_exact / consensus_total * 100, 1),
            "winner_accuracy": round(consensus_correct_winner / consensus_total * 100, 1),
            "exact_hits": consensus_correct_exact,
            "winner_hits": consensus_correct_winner,
            "total": consensus_total,
        }

    best_source = max(report["sources"].values(), key=lambda s: s["winner_accuracy"])
    worst_source = min(
        [s for s in report["sources"].values() if s["total"] >= 3],
        key=lambda s: s["winner_accuracy"], default=None,
    )
    if best_source["winner_accuracy"] > 0:
        report["recommendations"].append(
            f"Mejor fuente: {best_source['label']} ({best_source['winner_accuracy']}% ganador)"
        )
    if worst_source and worst_source["winner_accuracy"] < 40:
        report["recommendations"].append(
            f"Fuente debil: {worst_source['label']} ({worst_source['winner_accuracy']}% ganador) - considerar reducir peso"
        )
    if consensus_total > 0 and any(
        s["winner_accuracy"] > report["consensus"]["winner_accuracy"] + 5
        for s in report["sources"].values()
    ):
        report["recommendations"].append(
            "Alguna(s) fuente(s) superan al consenso individualmente - revisar pesos"
        )

    total_all = sum(s["total"] for s in report["sources"].values())
    total_exact = sum(s["exact_hits"] for s in report["sources"].values())
    total_winner = sum(s["winner_hits"] for s in report["sources"].values())
    n_sources = len([s for s in report["sources"].values() if s["total"] > 0])
    report["overall"] = {
        "avg_exact_accuracy": round(total_exact / total_all * 100, 1) if total_all else 0,
        "avg_winner_accuracy": round(total_winner / total_all * 100, 1) if total_all else 0,
        "active_sources": n_sources,
        "total_predictions_evaluated": total_all,
    }

    return report


def _compute_consensus(predictions: dict[str, str], weights: dict[str, float]) -> str:
    total_weight = sum(weights.values())
    score_weights: dict[str, float] = {}
    for key, score in predictions.items():
        w = weights.get(key, 1.0)
        score_weights[score] = score_weights.get(score, 0.0) + w

    best_score = max(score_weights, key=score_weights.get)
    return best_score


def main() -> None:
    print("=== Validando Predicciones ===")

    report = validate()

    if not report:
        print("  Validacion: SIN DATOS")
        return

    print(f"\n  Partidos evaluados: {report['matches_evaluated']}")
    print(f"  Fuentes activas: {report['overall']['active_sources']}/{len(SOURCE_KEYS)}")
    print(f"  Promedio exacto: {report['overall']['avg_exact_accuracy']:.1f}%")
    print(f"  Promedio ganador: {report['overall']['avg_winner_accuracy']:.1f}%")

    if report["consensus"]:
        print(f"\n  Consenso:")
        print(f"    Exacto: {report['consensus']['exact_accuracy']:.1f}%")
        print(f"    Ganador: {report['consensus']['winner_accuracy']:.1f}%")

    print(f"\n  Por fuente:")
    print(f"  {'Fuente':<20s} {'Exacta':>7s} {'Ganador':>8s} {'Muestras':>8s}")
    print(f"  {'-'*43}")
    for key in SOURCE_KEYS:
        s = report["sources"][key]
        if s["total"] > 0:
            print(f"  {s['label']:<20s} {s['exact_accuracy']:>6.1f}% {s['winner_accuracy']:>7.1f}% {s['total']:>4d}")

    if report["recommendations"]:
        print(f"\n  Recomendaciones:")
        for rec in report["recommendations"]:
            print(f"    - {rec}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"validation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n Reporte guardado: {out}")
    print("  Validacion: OK")


if __name__ == "__main__":
    main()
