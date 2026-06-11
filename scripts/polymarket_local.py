#!/usr/bin/env python3
"""
Agente Fuentes: Polymarket API (LOCAL - credenciales temporales)
Solo para testeo local. NO commitear este archivo.
"""

import os
import json
import requests
import base64
import hashlib
import hmac
import time
from datetime import datetime

# CREDENCIALES TEMPORALES - solo para testeo
# BORRAR después de usar o mover a variables de entorno
POLYMARKET_API_KEY = "019eb752-e18f-72b1-88c4-b97eecf6bfec"
POLYMARKET_SECRET = "mp82aKgyNCHB0ka9UetOl1DoJvmWICALGMh1NG2iSb4="
POLYMARKET_PASSPHRASE = "9ed67173cf38269a648c1d38b4556ceebd13523996d26bdb0ce49fe256eaf603"

class PolymarketAPI:
    def __init__(self):
        self.api_key = POLYMARKET_API_KEY
        self.secret = POLYMARKET_SECRET
        self.passphrase = POLYMARKET_PASSPHRASE
        self.base_url = "https://clob.polymarket.com"
        
    def generate_signature(self, timestamp, method, request_path, body=''):
        message = timestamp + method + request_path + body
        signature = hmac.new(
            base64.b64decode(self.secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def get_headers(self, method, path, body=''):
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
        """Obtener mercados activos del World Cup"""
        path = "/markets"
        headers = self.get_headers("GET", path)
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=headers,
                params={"active": "true", "limit": 200}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

def main():
    print("=== Polymarket API Test ===")
    
    api = PolymarketAPI()
    print(f"API Key: {api.api_key[:8]}...")
    
    # Obtener mercados
    markets = api.get_markets()
    
    if markets:
        print(f"\nMarkets found: {len(markets.get('data', []))}")
        
        # Guardar respuesta
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        with open(f"data/raw/polymarket_test_{timestamp}.json", "w") as f:
            json.dump(markets, f, indent=2)
        
        print(f"Data saved to data/raw/polymarket_test_{timestamp}.json")
        
        # Mostrar primeros mercados
        for i, market in enumerate(markets.get('data', [])[:5]):
            print(f"\n{i+1}. {market.get('question', 'N/A')}")
            print(f"   Slug: {market.get('market_slug', 'N/A')}")
    else:
        print("No markets retrieved or API error")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
