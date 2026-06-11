# Agente Fuentes - Prode Mundial 2026

## Rol
Buscar y extraer datos de predicciones de múltiples fuentes gratuitas cada 6 horas.

## Fuentes Prioritarias (gratuitas)

### 1. Polymarket (prode-market.pages.dev)
- Scraping de probabilidades por marcador
- Actualización cada 10 minutos según el sitio
- Método: BeautifulSoup/requests

### 2. Cup26 AI (cup26matches.com)
- API implícita vía el modelo open-source
- Ya integrado como fuente #9
- Actualizar si hay nuevas simulaciones

### 3. Football-Data.co.uk
- Historial de resultados gratuitos
- CSV descargables

### 4. FBref / Statbunker
- xG (expected goals) por equipo
- Forma reciente (últimos 5 partidos)

### 5. Transfermarkt
- Lesiones de jugadores clave
- Valor de mercado como proxy de fuerza

### 6. Reddit r/soccer
- Sentimiento de fanáticos
- Rumores de alineaciones

## Implementación

```python
# scripts/fetch_sources.py

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_polymarket():
    """Extraer probabilidades de prode-market.pages.dev"""
    url = "https://prode-market.pages.dev/?ver=dia"
    # Scraping dinámico con Selenium/Playwright
    pass

def fetch_football_data():
    """Descargar datos históricos"""
    url = "https://www.football-data.co.uk/mmz4281/2627/WC.csv"
    pass

def fetch_injuries():
    """Scrapear lesiones de Transfermarkt"""
    pass

def main():
    data = {
        "timestamp": datetime.now().isoformat(),
        "polymarket": fetch_polymarket(),
        "injuries": fetch_injuries(),
        "metadata": {"version": "1.0", "sources_checked": 6}
    }
    with open("data/raw/sources_" + datetime.now().strftime("%Y%m%d_%H%M") + ".json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
```

## Output
Guarda en `data/raw/sources_YYYYMMDD_HHMM.json`

## Métricas
- Fuentes activas: ≥ 4
- Datos obtenidos: ≥ 50 partidos con predicciones
- Tiempo de ejecución: < 30 min
