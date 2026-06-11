#!/usr/bin/env python3
"""
Agente Orquestador - Coordinar ciclo completo de mejora
"""

import subprocess
import sys
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "..")

AGENTS = [
    ("Fuentes", os.path.join(script_dir, "fetch_sources.py")),
    ("Modelo", os.path.join(script_dir, "recalibrate.py")),
    ("Valida", os.path.join(script_dir, "validate.py")),
    ("UI-UX", os.path.join(script_dir, "update_html.py")),
]

def run_agent(name, script):
    print(f"\n{'='*50}")
    print(f"AGENTE: {name}")
    print(f"{'='*50}")
    
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
        cwd=project_dir
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"WARN: {result.stderr}")
    
    return result.returncode == 0

def main():
    print(f"{'='*50}")
    print("ORQUESTADOR PRODE MUNDIAL 2026")
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    results = {}
    for name, script in AGENTS:
        results[name] = run_agent(name, script)
    
    print(f"\n{'='*50}")
    print("RESUMEN DE EJECUCION")
    print(f"{'='*50}")
    
    for name, success in results.items():
        status = "OK" if success else "FAIL"
        print(f"  {name}: {status}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\nTodos los agentes completaron OK")
        print("Ejecutando deploy...")
        
        deploy = subprocess.run(
            [sys.executable, "scripts/auto_deploy.py"],
            capture_output=True,
            text=True
        )
        print(deploy.stdout)
        
        if deploy.returncode == 0:
            print("\nDEPLOY OK")
        else:
            print("\nDEPLOY FAIL")
            sys.exit(1)
    else:
        print("\nAlgunos agentes fallaron. Abortando deploy.")
        sys.exit(1)

if __name__ == "__main__":
    main()
