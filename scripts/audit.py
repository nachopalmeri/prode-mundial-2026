#!/usr/bin/env python3
"""Audit script for all changes to the prediction pipeline."""

from __future__ import annotations

import json
import math
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def parse_score(sc: str) -> tuple[int, int]:
    parts = sc.split("-")
    return int(parts[0]), int(parts[1])

# ──────────────────────────────────────────────
# FASE 1: INJURY IMPACT ANALYSIS
# ──────────────────────────────────────────────

def simulate_goals(attack: float, defense: float, elo: float,
                   opp_elo: float, form: float, home_boost: float,
                   market_value_m: float, injury_penalty: float,
                   h2h_bonus: float, style_tempo: float,
                   draw_inflation: float = 0.55) -> tuple[float, float, float, float]:
    """Simplified version of predictive_engine scoring logic."""
    elo_diff = (elo - opp_elo) / 400.0
    raw_elo_exp = 1.0 / (1.0 + 10.0 ** (-elo_diff))
    # Expected goals from team strength
    base_exp = 0.5 + (raw_elo_exp - 0.5) * 1.8
    attack_f = (attack - 1.0) * 0.6
    defense_f = (1.0 - defense) * 0.5
    value_f = max(-0.15, min(0.15, (market_value_m - 150) / 3000))
    form_f = form * 0.3
    home_f = home_boost * 0.3
    inj_f = injury_penalty * 1.0
    tempo_f = (style_tempo - 1.0) * 0.15
    h2h_f = h2h_bonus * 0.2
    expected = base_exp + attack_f + defense_f + value_f + form_f + home_f - inj_f + tempo_f + h2h_f
    expected = max(0.1, min(4.5, expected))
    # Apply draw inflation (penalizes draws slightly as a structural factor)
    p_home_win = 0.5 + (expected - 1.0) * 0.18
    p_home_win = max(0.05, min(0.90, p_home_win))
    opponent_exp = max(0.1, min(4.5, 2.0 - expected))
    p_away_win = 0.5 + (opponent_exp - 1.0) * 0.18
    p_away_win = max(0.05, min(0.90, p_away_win))
    p_draw = 1.0 - p_home_win - p_away_win
    if p_draw < 0:
        total = p_home_win + p_away_win
        p_home_win /= total
        p_away_win /= total
        p_draw = 0.0
    return expected, opponent_exp, p_home_win, p_away_win


def phase1_injury_impact():
    print("=" * 72)
    print("FASE 1: IMPACTO DE LESIONES EN PREDICCIONES")
    print("=" * 72)

    priors = load_json(DATA_DIR / "config" / "team_strengths.json", {})
    injuries = load_json(DATA_DIR / "config" / "injuries.json", {})
    teams = priors.get("teams", {})

    print(f"\nEquipos con lesiones registradas: {len(injuries)}")
    print(f"Equipos en team_strengths: {len(teams)}")

    # Check which injured teams have strength data
    missing = [t for t in injuries if t not in teams]
    if missing:
        print(f"\n  [!]  Equipos con lesiones SIN datos de fortaleza: {missing}")

    # Compute impact per team
    print("\n  Equipo                     | out | dbt | injury_penalty | attack | base_goals | adj_goals | delta")
    print("  " + "-" * 100)
    impacts = []
    for team in sorted(injuries):
        ij = injuries[team]
        out_n = len(ij.get("out", []))
        dbt_n = len(ij.get("doubtful", []))
        penalty = min(1.2, 0.15 * out_n + 0.05 * dbt_n)

        if team in teams:
            raw = teams[team]
            base_penalty = float(raw.get("injury_penalty", 0))
            total_penalty = base_penalty + penalty
            attack = float(raw.get("attack", 1.0))
            base_exp = 1.0  # simplified baseline
            base_goals = base_exp - base_penalty
            adj_goals = base_exp - total_penalty
            delta = adj_goals - base_goals
        else:
            base_penalty = 0
            total_penalty = penalty
            base_goals = 1.0
            adj_goals = 1.0 - penalty
            delta = -penalty
            attack = 1.0

        impacts.append({
            "team": team,
            "out": out_n,
            "dbt": dbt_n,
            "penalty": penalty,
            "delta": delta,
        })
        print(f"  {team:28s} | {out_n:3d} | {dbt_n:3d} | {penalty:.2f}           | {attack:.2f}    | {base_goals:.2f}       | {adj_goals:.2f}     | {delta:+.2f}")

    max_delta = max(abs(i["delta"]) for i in impacts)
    avg_delta = sum(i["delta"] for i in impacts) / len(impacts) if impacts else 0
    heavy = [i for i in impacts if i["penalty"] >= 0.4]
    print(f"\n  Resumen:")
    print(f"    Equipos afectados:      {len(impacts)}")
    print(f"    Penalización promedio:   {sum(i['penalty'] for i in impacts)/len(impacts):.3f}")
    print(f"    Delta promedio en goles: {avg_delta:.3f}")
    print(f"    Máxima penalización:     {max_delta:.2f}")
    print(f"    Equipos con penalización severa (>=0.4): {len(heavy)}")
    for h in heavy:
        print(f"      - {h['team']}: {h['out']} out + {h['dbt']} doubtful = {h['penalty']:.2f}")
    print(f"    Riesgo de sobrepenalización: {'ALTO' if max_delta > 1.0 else 'CONTROLADO'}")
    return impacts


# ──────────────────────────────────────────────
# FASE 2: DK_PREDS VS MODELO
# ──────────────────────────────────────────────

def phase2_odds_audit():
    print("\n" + "=" * 72)
    print("FASE 2: AUDITORIA DK_PREDS VS MODELO")
    print("=" * 72)

    predictions = load_json(DATA_DIR / "model" / "latest_predictions.json", {})
    matches = predictions.get("matches", [])
    html_path = PROJECT_ROOT / "prode-mundial-2026.html"
    html = html_path.read_text(encoding="utf-8")
    import re
    m = re.search(r'const DK_PREDS = (\{[^}]+\})', html)
    if not m:
        print("  ERROR: No se encontro DK_PREDS en el HTML")
        return []
    dk_preds = json.loads(m.group(1))

    comparisons = []
    for match in matches:
        mid = str(match.get("id"))
        dk_score = dk_preds.get(mid)
        if not dk_score:
            continue

        model_score = match.get("consensus_pick")
        if not model_score:
            continue

        model_h, model_a = parse_score(model_score)
        dk_h, dk_a = parse_score(dk_score)

        model_outcome = "H" if model_h > model_a else ("A" if model_a > model_h else "D")
        dk_outcome = "H" if dk_h > dk_a else ("A" if dk_a > dk_h else "D")

        delta_h = abs(model_h - dk_h)
        delta_a = abs(model_a - dk_a)
        total_delta = delta_h + delta_a

        comparisons.append({
            "id": mid,
            "home": match["home"],
            "away": match["away"],
            "model": model_score,
            "dk": dk_score,
            "model_outcome": model_outcome,
            "dk_outcome": dk_outcome,
            "outcome_match": model_outcome == dk_outcome,
            "delta_h": delta_h,
            "delta_a": delta_a,
            "total_delta": total_delta,
        })

    comparisons.sort(key=lambda x: -x["total_delta"])

    matches_total = len(comparisons)
    if matches_total == 0:
        print("  No se pudieron comparar partidos")
        return []

    matches_coincide = sum(1 for c in comparisons if c["outcome_match"])
    score_exact = sum(1 for c in comparisons if c["model"] == c["dk"])

    match_pct = matches_coincide / matches_total * 100
    score_pct = score_exact / matches_total * 100
    avg_delta_h = sum(c["delta_h"] for c in comparisons) / matches_total
    avg_delta_a = sum(c["delta_a"] for c in comparisons) / matches_total
    avg_total = sum(c["total_delta"] for c in comparisons) / matches_total

    print(f"\n  Total partidos comparados: {matches_total}")
    print(f"  Coinciden en resultado (1X2): {matches_coincide}/{matches_total} ({match_pct:.1f}%)")
    print(f"  Coinciden en score exacto:   {score_exact}/{matches_total} ({score_pct:.1f}%)")
    print(f"  Discrepancia promedio goles L: {avg_delta_h:.2f}")
    print(f"  Discrepancia promedio goles V: {avg_delta_a:.2f}")
    print(f"  Discrepancia promedio total:   {avg_total:.2f}")

    print(f"\n  Top 10 mayores discrepancias:")
    print(f"  {'ID':>4s} {'Local':18s} {'Visitante':18s} {'Modelo':>8s} {'DK':>8s} {'Dif':>5s}")
    print(f"  " + "-" * 62)
    for c in comparisons[:10]:
        print(f"  {c['id']:>4s} {c['home']:18s} {c['away']:18s} {c['model']:>8s} {c['dk']:>8s} {c['total_delta']:.1f}")

    disagree = [c for c in comparisons if c["model_outcome"] != c["dk_outcome"]]
    print(f"\n  Desacuerdos de resultado (1X2): {len(disagree)}/{matches_total}")
    if disagree:
        print(f"  {'ID':>4s} {'Local':18s} {'Visitante':18s} {'Modelo':>8s} {'M 1X2':>5s} {'DK 1X2':>5s}")
        print(f"  " + "-" * 64)
        for c in disagree[:10]:
            print(f"  {c['id']:>4s} {c['home']:18s} {c['away']:18s} {c['model']:>8s} {c['model_outcome']:>5s} {c['dk_outcome']:>5s}")

    return comparisons


# ──────────────────────────────────────────────
# FASE 3: BACKTEST
# ──────────────────────────────────────────────

def phase3_backtest():
    print("\n" + "=" * 72)
    print("FASE 3: BACKTEST CONTRA RESULTADOS REALES")
    print("=" * 72)

    predictions = load_json(DATA_DIR / "model" / "latest_predictions.json", {})
    matches = predictions.get("matches", [])
    runtime = load_json(DATA_DIR / "runtime" / "results.json", {})

    # Compute pre-injury predictions (from accuracy data)
    accuracy_data = predictions.get("accuracy", {})

    # Build backtest
    results = runtime.get("results", {})
    n_played = len(results)
    print(f"\n  Partidos disputados: {n_played}")

    if n_played == 0:
        print("  No hay resultados para backtest")
        return

    # Get model predictions for played matches
    played_data = []
    for match in matches:
        mid = str(match.get("id"))
        if mid not in results:
            continue
        result = results[mid]
        consensus = match.get("consensus_pick")
        if not consensus:
            continue
        one_x_two = match.get("one_x_two", {})
        played_data.append({
            "id": mid,
            "home": match["home"],
            "away": match["away"],
            "result": result,
            "consensus_pick": consensus,
            "home_pct": one_x_two.get("home", 33.3),
            "draw_pct": one_x_two.get("draw", 33.3),
            "away_pct": one_x_two.get("away", 33.3),
        })

    correct_1x2 = 0
    correct_exact = 0
    brier_sum = 0.0
    log_loss_sum = 0.0
    total = len(played_data)

    for pd in played_data:
        rh, ra = parse_score(pd["result"])
        actual_1x2 = "H" if rh > ra else ("A" if ra > rh else "D")

        consensus = pd["consensus_pick"]
        ph, pa = parse_score(consensus)
        pred_1x2 = "H" if ph > pa else ("A" if pa > ph else "D")

        if pred_1x2 == actual_1x2:
            correct_1x2 += 1
        if consensus == pd["result"]:
            correct_exact += 1

        # Brier Score using stored probabilities
        h_prob = pd["home_pct"] / 100.0
        d_prob = pd["draw_pct"] / 100.0
        a_prob = pd["away_pct"] / 100.0

        actual_h = 1.0 if actual_1x2 == "H" else 0.0
        actual_d = 1.0 if actual_1x2 == "D" else 0.0
        actual_a = 1.0 if actual_1x2 == "A" else 0.0

        brier = (h_prob - actual_h)**2 + (d_prob - actual_d)**2 + (a_prob - actual_a)**2
        brier_sum += brier

        # Log Loss
        eps = 1e-15
        ll = 0.0
        for prob, actual in [(h_prob, actual_h), (d_prob, actual_d), (a_prob, actual_a)]:
            prob = max(eps, min(1-eps, prob))
            ll += actual * math.log(prob)
        log_loss_sum += -ll

    acc_1x2 = correct_1x2 / total * 100
    acc_exact = correct_exact / total * 100
    avg_brier = brier_sum / total
    avg_log_loss = log_loss_sum / total

    print(f"  Total evaluados:             {total}")
    print(f"  Exact Score Accuracy:        {acc_exact:.1f}% ({correct_exact}/{total})")
    print(f"  1X2 Accuracy:                {acc_1x2:.1f}% ({correct_1x2}/{total})")
    print(f"  Brier Score (avg):           {avg_brier:.4f}  (0=perfecto, 1=peor)")
    print(f"  Log Loss (avg):              {avg_log_loss:.4f}  (0=perfecto)")

    outcomes = Counter()
    for pd in played_data:
        h, a = parse_score(pd["result"])
        outcomes["H" if h > a else ("A" if a > h else "D")] += 1
    print(f"\n  Distribucion real de resultados:")
    print(f"    Local: {outcomes['H']} ({outcomes['H']/total*100:.0f}%)")
    print(f"    Empate: {outcomes['D']} ({outcomes['D']/total*100:.0f}%)")
    print(f"    Visitante: {outcomes['A']} ({outcomes['A']/total*100:.0f}%)")

    return {
        "exact_accuracy": acc_exact,
        "1x2_accuracy": acc_1x2,
        "brier_score": avg_brier,
        "log_loss": avg_log_loss,
    }


# ──────────────────────────────────────────────
# FASE 4: ELO AUDIT
# ──────────────────────────────────────────────

def phase4_elo_audit():
    print("\n" + "=" * 72)
    print("FASE 4: AUDITORIA DEL SISTEMA ELO")
    print("=" * 72)

    priors = load_json(DATA_DIR / "config" / "team_strengths.json", {})
    teams = priors.get("teams", {})
    applied_ids = priors.get("applied_elo_match_ids", [])

    print(f"\n  Equipos registrados: {len(teams)}")
    print(f"  Match IDs aplicados (applied_elo_match_ids): {len(applied_ids)}")

    # Check applied_ids consistency
    predictions = load_json(DATA_DIR / "model" / "latest_predictions.json", {})
    match_ids_all = sorted(set(str(m.get("id")) for m in predictions.get("matches", []) if m.get("id")))
    match_ids_played = [m.get("id") for m in predictions.get("matches", []) if m.get("played")]

    print(f"\n  Partidos en predictions: {len(match_ids_all)}")
    print(f"  Partidos marcados como played: {len(match_ids_played)}")
    if applied_ids and match_ids_played:
        extra_applied = set(applied_ids) - set(match_ids_played)
        missing_applied = set(match_ids_played) - set(applied_ids)
        if extra_applied:
            print(f"  [!]  IDs aplicados que NO están en played: {sorted(extra_applied)}")
        if missing_applied:
            print(f"  [!]  IDs played que NO se aplicaron: {sorted(missing_applied, key=int)}")
        if not extra_applied and not missing_applied:
            print(f"  [OK] applied_elo_match_ids coincide con played matches")
        else:
            print(f"  [!]  Inconsistencias detectadas")

    # Check for double application
    duplicates = [id_ for id_, count in Counter(applied_ids).items() if count > 1]
    if duplicates:
        print(f"  [X] DUPLICADOS en applied_elo_match_ids: {duplicates}")
    else:
        print(f"  [OK] No hay duplicados en applied_elo_match_ids")

    # ELO distribution
    elo_values = [t.get("elo", 1500) for t in teams.values()]
    if elo_values:
        print(f"\n  Distribución Elo actual:")
        print(f"    Mínimo: {min(elo_values):.0f}")
        print(f"    Máximo: {max(elo_values):.0f}")
        print(f"    Media: {sum(elo_values)/len(elo_values):.0f}")
        print(f"    Mediana: {sorted(elo_values)[len(elo_values)//2]:.0f}")

        # Check extreme Elo
        high_elo = [(n, t.get("elo", 0)) for n, t in sorted(teams.items(),
                     key=lambda x: -x[1].get("elo", 1500))[:5]]
        low_elo = [(n, t.get("elo", 0)) for n, t in sorted(teams.items(),
                    key=lambda x: x[1].get("elo", 1500))[:5]]
        print(f"\n    Top 5 Elo:")
        for name, elo in high_elo:
            updated = teams[name].get("elo_updated", "?")
            print(f"      {name:25s} {elo:.0f} (última actualización: {updated[:10] if updated != '?' else '?'})")
        print(f"    Bottom 5 Elo:")
        for name, elo in low_elo:
            updated = teams[name].get("elo_updated", "?")
            print(f"      {name:25s} {elo:.0f} (última actualización: {updated[:10] if updated != '?' else '?'})")

    # Check elo_updated field presence
    with_elo_date = sum(1 for t in teams.values() if "elo_updated" in t)
    without_elo_date = len(teams) - with_elo_date
    if without_elo_date > 0:
        print(f"\n  [!]  {without_elo_date} equipos sin elo_updated (nunca actualizados post-partido)")

    return {
        "total_teams": len(teams),
        "applied_ids": len(applied_ids),
        "duplicates": duplicates,
        "elo_range": (min(elo_values), max(elo_values)) if elo_values else (0, 0),
    }


# ──────────────────────────────────────────────
# FASE 6: GAP ANALYSIS
# ──────────────────────────────────────────────

def phase6_gap_analysis():
    print("\n" + "=" * 72)
    print("FASE 6: GAP ANALYSIS VS MODELOS PROFESIONALES")
    print("=" * 72)

    priors = load_json(DATA_DIR / "config" / "team_strengths.json", {})
    teams = priors.get("teams", {})

    # Count what variables we have
    present = Counter()
    for t in teams.values():
        for k in t:
            present[k] += 1

    print(f"\n  Variables disponibles en team_strengths ({len(teams)} equipos):")
    for var, count in sorted(present.items(), key=lambda x: -x[1]):
        pct = count / len(teams) * 100
        print(f"    {var:25s} {count:3d}/{len(teams)} ({pct:.0f}%)")

    # Variables missing vs professional models
    print(f"\n  Variables faltantes vs modelos profesionales:")
    print(f"  (FiveThirtyEight / ClubElo / Opta / StatsBomb / Betting Markets)")
    gaps = [
        ("xG (Expected Goals) por equipo", "Componente base de Opta/StatsBomb"),
        ("xGA (Expected Goals Against)", "Defensa medida en xG, no goles reales"),
        ("Deep completions / Passes into box", "Métrica de creación de chances"),
        ("Pressures / High turnovers", "Métrica de intensidad defensiva"),
        ("Set piece xG", "Goles esperados a balón parado"),
        ("Shot conversion rate", "Eficacia real vs esperada"),
        ("Player-level data", "Modelo necesita saber qué jugadores están disponibles"),
        ("Fatigue / days rest", "Equipos con menos descanso rinden peor"),
        ("Travel distance / altitude", "Factores logísticos reales"),
        ("Referee tendencies", "Algunos árbitros favorecen local o tarjetas"),
        ("Weather conditions", "Lluvia/calor afecta ritmo de juego"),
        ("Suspensions (yellow/red card accumulation)", "Diferenciado de lesiones"),
        ("Tournament pressure / knockout experience", "Factor psicológico"),
        ("Market consensus odds (closing lines)", "Mejor predictor único disponible"),
        ("Win/Loss streaks (morale)", "Más fino que simple form"),
        ("Possession stats", "Estilo de juego más granular"),
        ("Corners / cards markets", "Mercados relacionados"),
        ("Substitution impact", "Banco de suplentes profundo vs limitado"),
    ]
    for var, why in gaps:
        print(f"    [X] {var:45s} -> {why}")


# ──────────────────────────────────────────────
# RUN ALL
# ──────────────────────────────────────────────

if __name__ == "__main__":
    from collections import Counter

    phase1_injury_impact()
    phase2_odds_audit()
    phase3_backtest()
    phase4_elo_audit()
    phase6_gap_analysis()

    print("\n" + "=" * 72)
    print("FASE 5 y 7 requieren investigación externa")
    print("=" * 72)
