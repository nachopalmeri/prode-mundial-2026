#!/usr/bin/env python3
"""
Validar que el HTML esté correcto antes de deploy
"""

import sys

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, "..", "prode-mundial-2026.html")

def validate():
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    checks = [
        ("<!DOCTYPE html>", "DOCTYPE missing"),
        ("<html", "HTML tag missing"),
        ("</html>", "HTML closing tag missing"),
        ("<script", "Script tag missing"),
        ("matches.push", "Matches data missing"),
        ("function getConsensus", "getConsensus missing"),
        ("Chart.js", "Chart.js missing"),
        ("tab-dashboard", "Dashboard tab missing"),
        ("tab-noticias", "Noticias tab missing"),
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
        sys.exit(1)
    
    print("VALIDATION OK: HTML structure correct")
    print(f"  - File size: {len(html)} bytes")
    print(f"  - All required components present")
    sys.exit(0)

if __name__ == "__main__":
    validate()
