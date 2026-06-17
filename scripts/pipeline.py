#!/usr/bin/env python3
"""
Pipeline orquestador — corre todos los pasos en orden correcto
y reporta resultado. Llamado manualmente o por GitHub Actions.
"""

import subprocess, sys, os, json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

STEPS = [
    ("predictive_engine",    ["predictive_engine.py"],       False),
    ("recalibrate",           ["recalibrate.py"],             False),
    ("validate",              ["validate.py"],                False),
    ("embed_accuracy",        ["embed_accuracy.py"],          False),
    ("update_dashboard",      ["update_dynamic_dashboard.py"], False),
    ("embed_results",         ["embed_results.py"],           False),
    ("auto_update",           ["auto_update.py"],             False),
    ("validate_html",         ["validate_html.py"],           True),
]

def run_step(name, script, required):
    script_path = SCRIPT_DIR / script
    if not script_path.exists():
        print(f"  [{name}] script no encontrado: {script}")
        return not required
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, cwd=str(PROJECT_DIR)
    )
    ok = result.returncode == 0
    for line in result.stdout.strip().splitlines():
        print(f"  [{name}] {line}")
    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(f"  [{name}] ERR: {line}")
    if not ok and required:
        print(f"  [{name}] FAILED — abortando pipeline")
        return False
    if not ok:
        print(f"  [{name}] falló (no required, continuando)")
    return True

def main():
    print(f"Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {PROJECT_DIR}")
    print()

    results = {}
    for name, scripts, required in STEPS:
        for script in scripts:
            print(f"--- {name} ({script}) ---")
            ok = run_step(name, script, required)
            results[name] = ok
            if not ok and required:
                break

    print()
    print("=" * 50)
    print("RESUMEN PIPELINE")
    print("=" * 50)
    all_ok = True
    for name, ok in results.items():
        status = "OK" if ok else "FAIL"
        print(f"  {name:20s} {status}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\nPipeline completado exitosamente.")
    else:
        print("\nPipeline completado con fallos (ver arriba).")
        sys.exit(1)

if __name__ == "__main__":
    main()
