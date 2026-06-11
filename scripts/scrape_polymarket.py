#!/usr/bin/env python3
"""
Scrapear prode-market.pages.dev con Playwright
Extraer marcadores más probables de cada partido del World Cup 2026
"""

import json
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_polymarket():
    """Scrapear datos de prode-market.pages.dev"""
    
    url = "https://prode-market.pages.dev/?ver=grupo"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navegando a {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Esperar a que cargue el contenido
        page.wait_for_timeout(3000)
        
        # Extraer datos de cada partido
        matches = []
        
        # Buscar elementos que contengan la info de los partidos
        # La estructura parece ser: grupos con enlaces a Polymarket
        content = page.content()
        
        # Extraer texto visible
        text = page.inner_text("body")
        
        browser.close()
        
        return {"html": content[:5000], "text": text[:3000]}

def main():
    print("=== Scraping Polymarket ===")
    
    data = scrape_polymarket()
    
    os.makedirs("data/raw", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    with open(f"data/raw/polymarket_scrape_{timestamp}.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nTexto extraído (primeros 1000 chars):")
    print(data["text"][:1000])
    
    print(f"\nDatos guardados en: data/raw/polymarket_scrape_{timestamp}.json")
    print("=== Scraping Complete ===")

if __name__ == "__main__":
    main()
