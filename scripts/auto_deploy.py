#!/usr/bin/env python3
"""
Agente Deploy - Automatizar commit y deploy
"""

import subprocess
import sys
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "..")
html_path = os.path.join(project_dir, "prode-mundial-2026.html")

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd or project_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {cmd}\n{result.stderr}")
        return False
    print(f"OK: {cmd}")
    return True

def validate_html():
    """Validar que el HTML no esté roto"""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    checks = [
        ("<!DOCTYPE html>", "DOCTYPE missing"),
        ("<html", "HTML tag missing"),
        ("</html>", "HTML closing tag missing"),
        ("<script", "Script tag missing"),
        ("matches.push", "Matches data missing"),
        ("function getConsensus", "getConsensus missing"),
    ]
    
    html_lower = html.lower()
    errors = []
    for check, msg in checks:
        if check.lower() not in html_lower:
            errors.append(msg)
    
    if errors:
        print("VALIDATION FAIL:")
        for err in errors:
            print(f"  - {err}")
        return False
    
    print("VALIDATION OK: HTML structure correct")
    return True

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Validar
    if not validate_html():
        sys.exit(1)
    
    # 2. Git add
    if not run_command("git add -A"):
        sys.exit(1)
    
    # 3. Git commit
    if not run_command(f'git commit -m "Auto update {timestamp}"'):
        print("No changes to commit")
        sys.exit(0)
    
    # 4. Git push
    if not run_command("git push"):
        sys.exit(1)
    
    # 5. Vercel deploy
    if not run_command("npx vercel --prod --yes"):
        sys.exit(1)
    
    print(f"DEPLOY OK: {timestamp}")

if __name__ == "__main__":
    main()
