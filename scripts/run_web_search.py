#!/usr/bin/env python3
"""
run_web_search.py — Orquestador multi-agente de búsqueda web
Ejecuta los 6 agentes en paralelo, recopila datos, y lanza el pipeline.
"""

import subprocess, sys, json, os, glob, time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
RAW = BASE.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

AGENTS = [
    ("rankings", "agent_rankings.py"),
    ("polymarket", "agent_polymarket.py"),
    ("injuries", "agent_injuries.py"),
    ("predictions", "agent_predictions.py"),
    ("h2h", "agent_h2h.py"),
]

def run_agent(name, script, timeout=60):
    start = time.time()
    agent_path = BASE / script
    result = {"agent": name, "status": "error", "output": "", "elapsed": 0}
    try:
        r = subprocess.run(
            [sys.executable, str(agent_path)],
            capture_output=True, text=True, timeout=timeout
        )
        result["output"] = r.stdout + r.stderr
        result["status"] = "ok" if r.returncode == 0 else "error"
        result["returncode"] = r.returncode
    except subprocess.TimeoutExpired:
        result["output"] = f"TIMEOUT after {timeout}s"
    except Exception as e:
        result["output"] = str(e)
    result["elapsed"] = round(time.time() - start, 1)
    return result

def main():
    print("=" * 60)
    print("WEB SEARCH AGENTS — ORQUESTADOR")
    print(f"Start: {datetime.now().isoformat()}")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    results = []

    for name, script in AGENTS:
        print(f"\n--- Running {name} ({script}) ---")
        r = run_agent(name, script)
        print(f"Status: {r['status']} ({r['elapsed']}s)")
        print(r["output"][:500])
        results.append(r)

    print("\n" + "=" * 60)
    print("SUMMARY")
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"  OK: {ok_count}/{len(results)}")
    for r in results:
        print(f"  {r['agent']}: {r['status']} ({r['elapsed']}s)")
    print("=" * 60)

    # Collect raw data files and pass to integrator
    raw_files = sorted(glob.glob(str(RAW / f"*_{timestamp}.json")))
    print(f"\nRaw data files: {len(raw_files)}")

    # Run integrator
    print("\n--- Running integrator ---")
    integrator = BASE / "agent_integrator.py"
    try:
        r = subprocess.run(
            [sys.executable, str(integrator), timestamp],
            capture_output=True, text=True, timeout=60
        )
        print(r.stdout[-500:] if len(r.stdout) > 500 else r.stdout)
        if r.returncode != 0:
            print(f"Integrator errors: {r.stderr[:500]}")
    except Exception as e:
        print(f"Integrator failed: {e}")

    print("\nDone.")

if __name__ == "__main__":
    main()
