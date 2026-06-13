#!/usr/bin/env python3
"""
Ingresar resultados reales de partidos del Mundial 2026.
Guarda en data/runtime/results.json para que el sistema
de accuracy tracking pueda recalibrar pesos.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"

SCORE_RE = re.compile(r"^\d+-\d+$")
DAY_MAP = {"Jue": "Jueves", "Vie": "Viernes", "Sab": "Sabado",
           "Dom": "Domingo", "Lun": "Lunes", "Mar": "Martes", "Mie": "Miercoles"}


def load_results() -> dict:
    if RUNTIME_PATH.exists():
        return json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    return {"results": {}, "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "frozen_matches": {}, "news_adjustments": {},
            "seasons": {"accuracy_tracking": {"current_season": 1, "seasons": [
                {"id": 1, "name": "2026 World Cup", "match_count": 72,
                 "knockout_match_count": 32, "predicted_accuracy": None,
                 "actual_accuracy": None, "matches_played": 0,
                 "correct_picks": 0, "correct_exact_scores": 0}]}}}


def save_results(data: dict) -> None:
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    RUNTIME_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Resultados guardados en {RUNTIME_PATH}")


def parse_html_matches() -> list[dict]:
    """Parse match data from the dashboard HTML."""
    html = HTML_PATH.read_text(encoding="utf-8")
    raw_matches = re.findall(r"\{id:\d+,gr:\"[A-Z]\",[^}]+\}", html)
    matches = []
    for raw in raw_matches:
        pairs = re.findall(r'(\w+):(?:(\d+)|"([^"]*)")', raw)
        data = {k: (v2 or v3) for k, v2, v3 in pairs}
        matches.append({
            "id": int(data.get("id", 0)),
            "group": data.get("gr", ""),
            "date": data.get("d", ""),
            "time": data.get("h", ""),
            "home": data.get("a", ""),
            "away": data.get("b", ""),
        })
    return matches


def matches_for_date(matches: list[dict], target: str) -> list[dict]:
    """Filter matches by date string (e.g. 'Jue 11/6')."""
    return [m for m in matches if m["date"] == target]


def today_matches(matches: list[dict]) -> list[dict]:
    """Return matches scheduled for today."""
    now = datetime.now()
    target = now.strftime("%a %d/%m").replace(" 0", " ").replace("/0", "/")
    day_abbr = {"Mon": "Lun", "Tue": "Mar", "Wed": "Mie", "Thu": "Jue",
                "Fri": "Vie", "Sat": "Sab", "Sun": "Dom"}.get(now.strftime("%a"), "")
    date_str = f"{day_abbr} {now.day}/{now.month}"
    return matches_for_date(matches, date_str)


def show_matches(matches: list[dict], results: dict, title: str = "") -> None:
    if not matches:
        print("  (no hay partidos)")
        return
    if title:
        print(f"\n=== {title} ===")
    for m in matches:
        mid = str(m["id"])
        result = results.get("results", {}).get(mid)
        r_display = f" -> \033[92m{result}\033[0m" if result else "  \033[90m(sin resultado)\033[0m"
        print(f"  #{m['id']:2d} [{m['group']}] {m['home']:25s} vs {m['away']:25s}  {m['time']}{r_display}")


def interactive_mode() -> None:
    results_data = load_results()
    all_matches = parse_html_matches()

    today = today_matches(all_matches)
    show_matches(today, results_data, "PARTIDOS DE HOY")

    while True:
        print()
        mid_input = input("ID del partido (o Enter para salir): ").strip()
        if not mid_input:
            break

        try:
            match_id = int(mid_input)
        except ValueError:
            print("  ID invalido")
            continue

        match = next((m for m in all_matches if m["id"] == match_id), None)
        if not match:
            print(f"  No existe partido #{match_id}")
            continue

        mid = str(match_id)
        existing = results_data.get("results", {}).get(mid)
        if existing:
            print(f"  Ya tiene resultado: {existing} (se sobreescribira)")

        score = input(f"  Score ({match['home']} - {match['away']}): ").strip()
        if not SCORE_RE.match(score):
            print("  Formato invalido. Use: goles-goles (ej. 2-1)")
            continue

        results_data.setdefault("results", {})[mid] = score
        save_results(results_data)
        print(f"  \033[92mRegistrado: #{match_id} {match['home']} {score} {match['away']}\033[0m")

    print("\nResultados finales:")
    for mid, score in sorted(results_data.get("results", {}).items()):
        match = next((m for m in all_matches if str(m["id"]) == mid), None)
        if match:
            print(f"  #{mid} {match['home']} {score} {match['away']}")


def batch_mode(pairs: list[list[str]]) -> None:
    """Process --match ID SCORE pairs."""
    results_data = load_results()
    all_matches = parse_html_matches()
    saved = 0
    for parts in pairs:
        if len(parts) < 2:
            continue
        try:
            match_id = int(parts[0])
            score = parts[1]
        except ValueError:
            print(f"  Ignorado: {parts!r} (ID debe ser numero)")
            continue
        if not SCORE_RE.match(score):
            print(f"  Ignorado: {pair!r} (score debe ser goles-goles)")
            continue
        match = next((m for m in all_matches if m["id"] == match_id), None)
        mid = str(match_id)
        results_data.setdefault("results", {})[mid] = score
        saved += 1
        if match:
            print(f"  #{match_id} {match['home']} {score} {match['away']}")
        else:
            print(f"  #{match_id} (no encontrado en fixture) {score}")
    if saved:
        save_results(results_data)
        print(f"\n{saved} resultado(s) guardados")


def show_all_results() -> None:
    results_data = load_results()
    all_matches = parse_html_matches()
    played = results_data.get("results", {})
    if not played:
        print("No hay resultados registrados aun.")
        return
    print(f"\n=== RESULTADOS REGISTRADOS ({len(played)}) ===")
    for mid in sorted(played, key=int):
        score = played[mid]
        match = next((m for m in all_matches if str(m["id"]) == mid), None)
        if match:
            print(f"  #{mid} [{match['group']}] {match['home']:25s} {score:5s} {match['away']:25s}")


def run_pipeline() -> None:
    """Ejecutar el pipeline completo y hacer git commit+push."""
    print("\n=== Ejecutando pipeline ===")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "pipeline.py")],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parents[1])
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode == 0:
        # Auto commit + push
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        subprocess.run(["git", "add", "-A"], cwd=str(Path(__file__).resolve().parents[1]))
        proc = subprocess.run(
            ["git", "commit", "-m", f"Auto pipeline {ts}"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parents[1])
        )
        if "nothing to commit" in proc.stdout or "nothing to commit" in proc.stderr:
            print("  Sin cambios nuevos.")
        else:
            print(proc.stdout)
            push = subprocess.run(["git", "push"], capture_output=True, text=True,
                                  cwd=str(Path(__file__).resolve().parents[1]))
            if push.returncode == 0:
                print("  Push OK")
            else:
                print(f"  Push falló: {push.stderr}")
    else:
        print("  Pipeline falló — cambios no commiteados.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingresar resultados del Mundial 2026")
    parser.add_argument("--match", "-m", nargs=2, action="append", metavar=("ID", "SCORE"),
                        help="ID SCORE (ej: -m 1 2-0 -m 2 1-1)")
    parser.add_argument("--list", "-l", action="store_true", help="Mostrar resultados guardados")
    parser.add_argument("--today", "-t", action="store_true", help="Mostrar partidos de hoy")
    parser.add_argument("--pipeline", "-p", action="store_true", help="Solo correr pipeline sin pedir resultados")

    args = parser.parse_args()

    if args.pipeline:
        run_pipeline()
        return

    if args.list:
        show_all_results()
        return

    if args.today:
        results_data = load_results()
        all_matches = parse_html_matches()
        show_matches(today_matches(all_matches), results_data, "PARTIDOS DE HOY")
        return

    if args.match:
        batch_mode(args.match)
        if input("\nCorrer pipeline ahora? (s/N): ").strip().lower() == "s":
            run_pipeline()
        return

    interactive_mode()
    # Despues de modo interactivo, preguntar si correr pipeline
    if input("\nCorrer pipeline ahora? (s/N): ").strip().lower() == "s":
        run_pipeline()


if __name__ == "__main__":
    main()
