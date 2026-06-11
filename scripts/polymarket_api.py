#!/usr/bin/env python3
"""
Agente Fuentes: Polymarket API Integration
Extraer probabilidades de mercado para cada partido del Mundial 2026
"""

import os
import json
import requests
import base64
import hashlib
import hmac
import time
from datetime import datetime

class PolymarketAPI:
    """Cliente para la API de Polymarket"""
    
    def __init__(self):
        self.api_key = os.getenv('POLYMARKET_API_KEY', '')
        self.secret = os.getenv('POLYMARKET_SECRET', '')
        self.passphrase = os.getenv('POLYMARKET_PASSPHRASE', '')
        self.base_url = "https://clob.polymarket.com"
        
    def generate_signature(self, timestamp, method, request_path, body=''):
        """Generar firma HMAC para autenticación"""
        message = timestamp + method + request_path + body
        signature = hmac.new(
            base64.b64decode(self.secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def get_headers(self, method, path, body=''):
        """Generar headers con autenticación"""
        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(timestamp, method, path, body)
        
        return {
            'POLYMARKET_API_KEY': self.api_key,
            'POLYMARKET_SIGNATURE': signature,
            'POLYMARKET_TIMESTAMP': timestamp,
            'POLYMARKET_PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_markets(self):
        """Obtener todos los mercados del World Cup"""
        path = "/markets"
        headers = self.get_headers("GET", path)
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=headers,
                params={"active": "true", "limit": 100}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return None
    
    def get_market(self, market_id):
        """Obtener detalle de un mercado específico"""
        path = f"/markets/{market_id}"
        headers = self.get_headers("GET", path)
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_order_book(self, token_id):
        """Obtener order book para calcular probabilidad"""
        path = f"/book/{token_id}"
        headers = self.get_headers("GET", path)
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None


def extract_world_cup_markets(markets_data):
    """Filtrar solo mercados del World Cup"""
    if not markets_data or 'data' not in markets_data:
        return []
    
    wc_markets = []
    for market in markets_data.get('data', []):
        description = market.get('description', '').lower()
        slug = market.get('market_slug', '').lower()
        question = market.get('question', '').lower()
        
        # Filtrar por keywords del World Cup
        wc_keywords = ['world cup', 'fifa', 'fifwc', 'mundial']
        if any(kw in description or kw in slug or kw in question for kw in wc_keywords):
            wc_markets.append(market)
    
    return wc_markets


def calculate_probability_from_orderbook(orderbook):
    """Calcular probabilidad implícita del order book"""
    if not orderbook:
        return None
    
    # Calcular precio medio entre best bid y best ask
    bids = orderbook.get('bids', [])
    asks = orderbook.get('asks', [])
    
    if bids and asks:
        best_bid = float(bids[0].get('price', 0))
        best_ask = float(asks[0].get('price', 0))
        midpoint = (best_bid + best_ask) / 2
        return round(midpoint * 100, 1)
    elif bids:
        return round(float(bids[0].get('price', 0)) * 100, 1)
    elif asks:
        return round(float(asks[0].get('price', 0)) * 100, 1)
    
    return None


def main():
    """Función principal para ejecutar como script"""
    print("=== Agente Fuentes: Polymarket API ===")
    
    api = PolymarketAPI()
    
    if not api.api_key:
        print("WARN: No API credentials found. Set POLYMARKET_API_KEY env var.")
        print("Falling back to manual input mode...")
        return
    
    print(f"API Key configured: {api.api_key[:8]}...")
    
    # Obtener mercados
    markets = api.get_markets()
    if markets:
        wc_markets = extract_world_cup_markets(markets)
        print(f"Found {len(wc_markets)} World Cup markets")
        
        # Guardar datos
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"data/raw/polymarket_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "markets_found": len(wc_markets),
                "markets": wc_markets[:10]  # Primeros 10 para no saturar
            }, f, indent=2)
        
        print(f"Data saved to: {output_file}")
    else:
        print("No markets retrieved")
    
    print("Agente Fuentes (Polymarket): OK")


if __name__ == "__main__":
    main()
