# Agente Deploy - Prode Mundial 2026

## Rol
Automatizar el commit a GitHub y deploy a Vercel sin intervención manual.

## Workflow de Deploy

```
1. Verificar cambios
   │
   ├──► ¿Hay archivos modificados?
   │   ├──► No → Terminar
   │   └──► Sí → Continuar
   │
   ├──► Validar HTML
   │   └──► python scripts/validate_html.py
   │
   ├──► Commit a GitHub
   │   └──► git add -A && git commit -m "Auto: update [timestamp]"
   │
   ├──► Push a origin/main
   │   └──► git push
   │
   └──► Deploy a Vercel
       └──► npx vercel --prod --yes
```

## Implementación

```python
# scripts/auto_deploy.py

import subprocess
import sys
from datetime import datetime

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {cmd}\n{result.stderr}")
        return False
    print(f"OK: {cmd}")
    return True

def validate_html():
    """Validar que el HTML no esté roto"""
    with open("prode-mundial-2026.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    checks = [
        ("<!DOCTYPE html>", "DOCTYPE missing"),
        ("<html", "HTML tag missing"),
        ("</html>", "HTML closing tag missing"),
        ("<script", "Script tag missing"),
        ("matches.push", "Matches data missing"),
        ("function getConsensus", "getConsensus missing"),
    ]
    
    for check, msg in checks:
        if check not in html:
            print(f"VALIDATION FAIL: {msg}")
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
```

## Configuración de Vercel

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "*.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/prode-mundial-2026.html"
    }
  ]
}
```

## Variables de Entorno (GitHub Secrets)
- `VERCEL_TOKEN`: Token de deploy
- `VERCEL_ORG_ID`: ID de organización
- `VERCEL_PROJECT_ID`: ID del proyecto

## Output
- URL de deploy: https://pisculabs.vercel.app/prode-mundial-2026.html
- Status: OK / FAIL

## Métricas
- Tiempo de deploy: < 5 min
- Uptime: 99.9%
- Rollback time: < 2 min
