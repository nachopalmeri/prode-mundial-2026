# Agente Valida - Prode Mundial 2026

## Rol
Validar la precisión de las predicciones vs resultados reales y generar reportes de calidad.

## Métricas de Validación

### 1. Accuracy Global
- Porcentaje de predicciones correctas (exacto + ganador)
- Benchmark: random = 33%, betting market = 52%

### 2. Accuracy por Fuente
- Ranking de fuentes más precisas
- Identificar sesgos (siempre predice favoritos, etc.)

### 3. Accuracy por Tipo de Partido
- Favorito claro (Elo diff > 200)
- Partido parejo (Elo diff < 100)
- Underdogs sorpresa

### 4. Puntos Acumulados (Prode)
- Simular cuántos puntos hubiera obtenido cada fuente
- Comparar vs consenso ponderado

## Reporte de Salida

```json
{
  "validation_date": "2026-06-20T12:00:00Z",
  "matches_evaluated": 24,
  "sources_accuracy": {
    "cascade": {"exact": 12, "winner": 8, "wrong": 4, "points": 52},
    "chatgpt": {"exact": 10, "winner": 9, "wrong": 5, "points": 48},
    "1960tips": {"exact": 15, "winner": 6, "wrong": 3, "points": 57},
    "consensus": {"exact": 14, "winner": 7, "wrong": 3, "points": 56}
  },
  "insights": [
    "1960Tips tiene mejor accuracy en favoritos claros",
    "Cup26 AI acierta más en partidos parejos",
    "El consenso ponderado supera al promedio simple en 8%"
  ],
  "recommendations": [
    "Aumentar peso de 1960Tips a 1.7",
    "Disminuir peso de Fansided a 0.6"
  ]
}
```

## Implementación

```python
# scripts/validate.py

import json
from datetime import datetime

def validate_predictions(results_file, predictions_file):
    with open(results_file) as f:
        results = json.load(f)
    with open(predictions_file) as f:
        predictions = json.load(f)
    
    report = {
        "validation_date": datetime.now().isoformat(),
        "matches_evaluated": len(results),
        "sources_accuracy": {},
        "insights": [],
        "recommendations": []
    }
    
    # Calcular accuracy por fuente
    for source in predictions["sources"]:
        exact = 0
        winner = 0
        wrong = 0
        points = 0
        
        for match_id, pred in source["predictions"].items():
            real = results.get(match_id)
            if not real:
                continue
            
            if pred == real:
                exact += 1
                points += 3
            elif get_winner(pred) == get_winner(real):
                winner += 1
                points += 1
            else:
                wrong += 1
        
        report["sources_accuracy"][source["id"]] = {
            "exact": exact, "winner": winner, "wrong": wrong, "points": points
        }
    
    # Generar insights
    best_source = max(report["sources_accuracy"], key=lambda x: report["sources_accuracy"][x]["points"])
    report["insights"].append(f"{best_source} lidera con {report['sources_accuracy'][best_source]['points']} puntos")
    
    # Generar recomendaciones
    for source_id, stats in report["sources_accuracy"].items():
        accuracy = (stats["exact"] + stats["winner"]) / report["matches_evaluated"]
        if accuracy > 0.6:
            report["recommendations"].append(f"Aumentar peso de {source_id}")
        elif accuracy < 0.4:
            report["recommendations"].append(f"Revisar {source_id} - accuracy baja")
    
    return report
```

## Output
- `data/reports/validation_YYYYMMDD.json`
- Post en dashboard del HTML

## Alertas
- Si accuracy del consenso < 45% → Alerta roja
- Si una fuente cae < 30% → Desactivar temporalmente
- Si 3+ partidos consecutivos mal → Revisar modelo
