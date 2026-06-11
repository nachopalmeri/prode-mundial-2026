#!/usr/bin/env python3
"""
Scrapear prode-market.pages.dev con Playwright - versión completa
Extraer TODOS los marcadores más probables de los 72 partidos
"""

import json
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_polymarket():
    url = "https://prode-market.pages.dev/?ver=grupo"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navegando a {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)  # Esperar carga JS
        
        # Extraer TODO el texto visible
        text = page.inner_text("body")
        
        browser.close()
        return text

def extract_matches(text):
    """Extraer marcadores más probables del texto scrapeado"""
    matches = {}
    
    # Patrón para encontrar: "Más probable · XX%\nEl resultado más probable es X-Y"
    pattern = r'Más probable · (\d+)%\s*\n\s*El resultado más probable es (\d+-\d+)'
    
    found = re.findall(pattern, text)
    
    # También buscar el patrón alternativo
    pattern2 = r'El resultado más probable es (\d+-\d+) \((\d+)% de probabilidad\)'
    found2 = re.findall(pattern2, text)
    
    print(f"Patrón 1 encontrados: {len(found)}")
    print(f"Patrón 2 encontrados: {len(found2)}")
    
    # Combinar resultados
    all_scores = []
    for _, score in found:
        all_scores.append(score)
    for score, _ in found2:
        all_scores.append(score)
    
    return all_scores

def main():
    print("=== Scraping Polymarket Completo ===")
    
    text = scrape_polymarket()
    
    # Guardar texto completo
    os.makedirs("data/raw", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    with open(f"data/raw/polymarket_full_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    # Extraer marcadores
    scores = extract_matches(text)
    
    print(f"\nMarcadores extraídos: {len(scores)}")
    for i, score in enumerate(scores[:10]):
        print(f"  Partido {i+1}: {score}")
    
    # Guardar JSON
    predictions = {str(i+1): score for i, score in enumerate(scores)}
    
    with open(f"data/raw/polymarket_predictions_{timestamp}.json", "w") as f:
        json.dump(predictions, f, indent=2)
    
    print(f"\nDatos guardados:")
    print(f"  - Texto: data/raw/polymarket_full_{timestamp}.txt")
    print(f"  - JSON: data/raw/polymarket_predictions_{timestamp}.json")
    print("=== Scraping Complete ===")

if __name__ == "__main__":
    main()
