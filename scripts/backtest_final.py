#!/usr/bin/env python3
"""Full backtest with pre/post comparison."""
import json, math, sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def parse_score(sc):
    parts = sc.split("-")
    return int(parts[0]), int(parts[1])

def outcome(sc):
    h, a = parse_score(sc)
    return "H" if h > a else ("A" if a > h else "D")

print("=" * 72)
print("BACKTEST COMPLETO vs RESULTADOS REALES")
print("=" * 72)

predictions = load_json(DATA_DIR / "model" / "latest_predictions.json")
matches = predictions.get("matches", [])
runtime = load_json(DATA_DIR / "runtime" / "results.json")
results = runtime.get("results", {})

n_played = len(results)
print(f"\nPartidos disputados: {n_played}")

played = []
for m in matches:
    mid = str(m.get("id"))
    if mid not in results:
        continue
    consensus = m.get("consensus_pick")
    if not consensus:
        continue
    one_x_two = m.get("one_x_two", {})
    played.append({
        "id": int(mid), "home": m["home"], "away": m["away"],
        "result": results[mid],
        "consensus": consensus,
        "h_pct": one_x_two.get("home", 33.3),
        "d_pct": one_x_two.get("draw", 33.3),
        "a_pct": one_x_two.get("away", 33.3),
    })

played.sort(key=lambda x: x["id"])

# --- Metrics ---
correct_1x2 = 0
correct_exact = 0
brier_sum = 0.0
log_loss_sum = 0.0
total = len(played)
eps = 1e-15

table_rows = []

for p in played:
    rh, ra = parse_score(p["result"])
    actual_1x2 = "H" if rh > ra else ("A" if ra > rh else "D")

    ph, pa = parse_score(p["consensus"])
    pred_1x2 = "H" if ph > pa else ("A" if pa > ph else "D")

    match_1x2 = pred_1x2 == actual_1x2
    match_exact = p["consensus"] == p["result"]

    if match_1x2:
        correct_1x2 += 1
    if match_exact:
        correct_exact += 1

    h_prob = p["h_pct"] / 100.0
    d_prob = p["d_pct"] / 100.0
    a_prob = p["a_pct"] / 100.0

    actual_h = 1.0 if actual_1x2 == "H" else 0.0
    actual_d = 1.0 if actual_1x2 == "D" else 0.0
    actual_a = 1.0 if actual_1x2 == "A" else 0.0

    brier = (h_prob - actual_h)**2 + (d_prob - actual_d)**2 + (a_prob - actual_a)**2
    brier_sum += brier

    ll = 0.0
    for prob, actual in [(h_prob, actual_h), (d_prob, actual_d), (a_prob, actual_a)]:
        prob = max(eps, min(1 - eps, prob))
        ll += actual * math.log(prob)
    log_loss_sum += -ll

    table_rows.append({
        "id": p["id"], "home": p["home"], "away": p["away"],
        "result": p["result"], "predict": p["consensus"],
        "1x2": "OK" if match_1x2 else "XX",
        "exact": "OK" if match_exact else "",
    })

acc_1x2 = correct_1x2 / total * 100
acc_exact = correct_exact / total * 100
avg_brier = brier_sum / total
avg_log_loss = log_loss_sum / total

print(f"\n{'='*72}")
print(f"MÉTRICAS GLOBALES ({total} partidos)")
print(f"{'='*72}")
print(f"  1X2 Accuracy:         {acc_1x2:.1f}% ({correct_1x2}/{total})")
print(f"  Exact Score Accuracy: {acc_exact:.1f}% ({correct_exact}/{total})")
print(f"  Brier Score (avg):    {avg_brier:.4f}  (0=perfecto, 1=peor)")
print(f"  Log Loss (avg):       {avg_log_loss:.4f}  (0=perfecto)")

print(f"\n{'='*72}")
print(f"DETALLE PARTIDO POR PARTIDO")
print(f"{'='*72}")
print(f" {'ID':>3s} {'Local':20s} {'Visitante':20s} {'Resultado':>9s} {'Prediccion':>10s} {'1X2':>3s} {'Exacto':>6s} {'Prob L':>6s} {'Prob E':>6s} {'Prob V':>6s}")
print(f" {'---':>3s} {'----':20s} {'---------':20s} {'--------':>9s} {'----------':>10s} {'---':>3s} {'------':>6s} {'------':>6s} {'------':>6s} {'------':>6s}")
for r in table_rows:
    p = next(x for x in played if x["id"] == r["id"])
    print(f" {r['id']:3d} {r['home']:20s} {r['away']:20s} {r['result']:>9s} {r['predict']:>10s} {r['1x2']:>3s} {r['exact']:>6s} {p['h_pct']:5.1f}% {p['d_pct']:5.1f}% {p['a_pct']:5.1f}%")

# Comparison with pre-audit version
print(f"\n{'='*72}")
print(f"COMPARATIVA vs VERSION ANTERIOR (Audit Fase 3)")
print(f"{'='*72}")
print(f"")
print(f"  {'Metrica':30s} {'Antes':>10s} {'Ahora':>10s} {'Delta':>10s}")
print(f"  {'-------':30s} {'-----':>10s} {'-----':>10s} {'-----':>10s}")
print(f"  {'1X2 Accuracy':30s} {'95.0%':>10s} {f'{acc_1x2:.1f}%':>10s} {f'{acc_1x2 - 95.0:+.1f}%':>10s}")
print(f"  {'Exact Score Accuracy':30s} {'60.0%':>10s} {f'{acc_exact:.1f}%':>10s} {f'{acc_exact - 60.0:+.1f}%':>10s}")
print(f"  {'Brier Score':30s} {'0.2193':>10s} {f'{avg_brier:.4f}':>10s} {f'{avg_brier - 0.2193:+.4f}':>10s}")
print(f"  {'Log Loss':30s} {'0.4383':>10s} {f'{avg_log_loss:.4f}':>10s} {f'{avg_log_loss - 0.4383:+.4f}':>10s}")
