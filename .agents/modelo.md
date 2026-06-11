# Agente Modelo - Prode Mundial 2026

## Rol
Recalcular los pesos del consenso ponderado basándose en la precisión histórica de cada fuente.

## Algoritmo de Auto-ML para Pesos

```python
# scripts/recalibrate.py

import json
import numpy as np
from datetime import datetime

def calculate_accuracy(source_id, historical_results):
    """
    Calcular accuracy de una fuente:
    - Exact score: 3 pts
    - Winner correct: 1 pt
    - Wrong: 0 pts
    - Normalizado a 0-100%
    """
    total_points = 0
    max_points = len(historical_results) * 3
    
    for match in historical_results:
        pred = match['predictions'][source_id]
        real = match['result']
        
        if pred == real:
            total_points += 3  # Exact
        elif get_winner(pred) == get_winner(real):
            total_points += 1  # Winner
    
    return (total_points / max_points) * 100

def adjust_weights(current_weights, accuracies):
    """
    Ajustar pesos basado en accuracy:
    - Fuente con accuracy > 60%: peso +0.2
    - Fuente con accuracy 40-60%: peso sin cambio
    - Fuente con accuracy < 40%: peso -0.2 (mínimo 0.5)
    - Máximo peso: 2.0
    """
    new_weights = {}
    for source, weight in current_weights.items():
        acc = accuracies.get(source, 50)
        if acc > 60:
            new_weights[source] = min(2.0, weight + 0.2)
        elif acc < 40:
            new_weights[source] = max(0.5, weight - 0.2)
        else:
            new_weights[source] = weight
    return new_weights

def generate_predictions(matches, weights):
    """Generar nuevo consenso ponderado para partidos pendientes"""
    pass

def main():
    # Cargar pesos actuales
    with open("data/model/weights.json") as f:
        weights = json.load(f)
    
    # Cargar resultados históricos
    with open("data/historical/results.json") as f:
        historical = json.load(f)
    
    # Calcular accuracy por fuente
    accuracies = {
        source: calculate_accuracy(source, historical)
        for source in weights.keys()
    }
    
    # Ajustar pesos
    new_weights = adjust_weights(weights, accuracies)
    
    # Guardar
    with open("data/model/weights_" + datetime.now().strftime("%Y%m%d") + ".json", "w") as f:
        json.dump({
            "weights": new_weights,
            "accuracies": accuracies,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    # Actualizar HTML
    update_html_weights(new_weights)

if __name__ == "__main__":
    main()
```

## Pesos Actuales (baseline)
```json
{
  "c": 1.0, "g": 1.0, "m": 1.0,
  "fs": 0.8, "esp": 1.3, "yh": 0.8,
  "t": 1.5, "e": 1.5, "cup": 1.4
}
```

## Output
- `data/model/weights_YYYYMMDD.json`
- HTML actualizado con nuevos pesos

## Métricas
- Accuracy del consenso: > 55%
- Mejora por iteración: +3%
- Overfitting: < 5%
