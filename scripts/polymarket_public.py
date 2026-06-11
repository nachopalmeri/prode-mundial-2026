#!/usr/bin/env python3
"""
Polymarket Public API - Sin autenticación
Usar endpoints públicos para obtener datos del World Cup
"""

import requests
import json
import os
from datetime import datetime

def get_world_cup_events():
    """Obtener eventos del World Cup desde la API pública"""
    
    # Intentar endpoint de gamma (API pública de Polymarket)
    url = "https://gamma-api.polymarket.com/events"
    
    params = {
        "active": "true",
        "archived": "false",
        "closed": "false",
        "limit": "100",
        "offset": "0",
        "order": "asc",
        "sort_by": "startDate",
        "tag_slug": "soccer"  # o "world-cup"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    print("=== Polymarket Public API Test ===")
    
    events = get_world_cup_events()
    
    if events:
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        with open(f"data/raw/polymarket_public_{timestamp}.json", "w") as f:
            json.dump(events, f, indent=2)
        
        print(f"\nData saved!")
        
        # Mostrar eventos
        if isinstance(events, list):
            for i, event in enumerate(events[:10]):
                title = event.get('title', 'N/A')
                print(f"\n{i+1}. {title}")
                markets = event.get('markets', [])
                for m in markets[:3]:
                    print(f"   - {m.get('question', 'N/A')}")
        elif isinstance(events, dict) and 'data' in events:
            for i, event in enumerate(events['data'][:10]):
                title = event.get('title', 'N/A')
                print(f"\n{i+1}. {title}")
    else:
        print("No events retrieved")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
