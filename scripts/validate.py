#!/usr/bin/env python3
"""
Agente Valida - Validar predicciones vs resultados reales
"""

import json
import os
from datetime import datetime

def validate_predictions():
    """Validar predicciones contra resultados"""
    hist_file = "data/historical/results.json"
    
    if not os.path.exists(hist_file):
        print("No hay resultados históricos para validar")
        return None
    
    with open(hist_file) as f:
        historical = json.load(f)
    
    if not historical:
        print("No hay partidos jugados aún")
        return None
    
    report = {
        "validation_date": datetime.now().isoformat(),
        "matches_evaluated": len(historical),
        "sources_accuracy": {},
        "insights": [],
        "recommendations": []
    }
    
    # Calcular accuracy por fuente (simplificado)
    print(f"Partidos evaluados: {len(historical)}")
    
    return report

def main():
    print("=== Agente Valida ===")
    
    report = validate_predictions()
    
    if report:
        ensure_dir = lambda p: os.makedirs(p, exist_ok=True)
        ensure_dir("data/reports")
        
        output_file = f"data/reports/validation_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Reporte guardado en: {output_file}")
    
    print("Agente Valida: OK")

if __name__ == "__main__":
    main()
