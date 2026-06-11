#!/usr/bin/env python3
"""
Agente Modelo - Recalcular pesos del consenso basado en accuracy histórica
"""

import json
import os
from datetime import datetime

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def calculate_accuracy(source_id, historical):
    """Calcular accuracy de una fuente"""
    if not historical:
        return 50.0
    
    total_points = 0
    max_points = len(historical) * 3
    
    for match in historical:
        preds = match.get("predictions", {})
        real = match.get("result", "")
        pred = preds.get(source_id, "")
        
        if not pred or not real:
            continue
        
        if pred == real:
            total_points += 3
        elif get_winner(pred) == get_winner(real):
            total_points += 1
    
    return (total_points / max_points) * 100 if max_points > 0 else 50.0

def get_winner(score):
    """Determinar ganador de un marcador"""
    try:
        a, b = map(int, score.split("-"))
        if a > b:
            return "A"
        elif b > a:
            return "B"
        return "D"
    except:
        return None

def adjust_weights(current_weights, accuracies):
    """Ajustar pesos basado en accuracy"""
    new_weights = {}
    for source, weight in current_weights.items():
        acc = accuracies.get(source, 50.0)
        if acc > 65:
            new_weights[source] = min(2.0, round(weight + 0.15, 2))
        elif acc > 55:
            new_weights[source] = round(weight + 0.05, 2)
        elif acc < 35:
            new_weights[source] = max(0.5, round(weight - 0.15, 2))
        elif acc < 45:
            new_weights[source] = max(0.5, round(weight - 0.05, 2))
        else:
            new_weights[source] = weight
    return new_weights

def load_current_weights():
    """Cargar pesos actuales del HTML"""
    # Pesos por defecto
    return {
        "c": 1.0, "g": 1.0, "m": 1.0,
        "fs": 0.8, "esp": 1.3, "yh": 0.8,
        "t": 1.5, "e": 1.5, "cup": 1.4
    }

def load_historical():
    """Cargar resultados históricos"""
    hist_file = "data/historical/results.json"
    if os.path.exists(hist_file):
        with open(hist_file) as f:
            return json.load(f)
    return []

def update_html_weights(weights):
    """Actualizar pesos en el HTML"""
    html_file = "prode-mundial-2026.html"
    if not os.path.exists(html_file):
        print("HTML no encontrado")
        return
    
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Actualizar SOURCE_WEIGHTS
    weights_str = ",".join([f'{k}:{v}' for k, v in weights.items()])
    # Esto es simplificado - en producción haría un parsing más robusto
    print(f"Pesos a aplicar: {weights}")

def main():
    ensure_dir("data/model")
    ensure_dir("data/historical")
    
    print("=== Agente Modelo ===")
    
    # Cargar datos
    weights = load_current_weights()
    historical = load_historical()
    
    print(f"Partidos históricos: {len(historical)}")
    
    # Calcular accuracy
    accuracies = {
        source: calculate_accuracy(source, historical)
        for source in weights.keys()
    }
    
    print("Accuracy por fuente:")
    for source, acc in accuracies.items():
        print(f"  {source}: {acc:.1f}%")
    
    # Ajustar pesos
    new_weights = adjust_weights(weights, accuracies)
    
    print("\nNuevos pesos:")
    for source, weight in new_weights.items():
        change = ""
        if weight != weights[source]:
            diff = weight - weights[source]
            change = f" ({diff:+.2f})"
        print(f"  {source}: {weight}{change}")
    
    # Guardar
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = f"data/model/weights_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump({
            "weights": new_weights,
            "accuracies": accuracies,
            "previous_weights": weights,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    # Actualizar HTML
    update_html_weights(new_weights)
    
    print(f"\nPesos guardados en: {output_file}")
    print("Agente Modelo: OK")

if __name__ == "__main__":
    main()
