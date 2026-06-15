#!/usr/bin/env python3
"""
Actualiza resultados reales del Mundial 2026 obtenidos de fuentes web (FIFA, Olympics.com, MARCA, etc.)
Reemplaza datos incorrectos/inventados con resultados confirmados.
"""
import json, re, os, math
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===== RESULTADOS REALES CONFIRMADOS (web: FIFA, Olympics.com, MARCA, NBC Sports, Bundesliga) =====
REAL_RESULTS = {
    # Matchdays 1-12: confirmados
    "1": "2-0",   # Mexico 2-0 South Africa (11 Jun)
    "2": "2-1",   # South Korea 2-1 Czechia (11 Jun)
    "3": "1-1",   # Canada 1-1 Bosnia (12 Jun)
    "4": "4-1",   # USA 4-1 Paraguay (12 Jun)
    "5": "1-1",   # Qatar 1-1 Switzerland (13 Jun)
    "6": "1-1",   # Brazil 1-1 Morocco (13 Jun)
    "7": "0-1",   # Haiti 0-1 Scotland (13 Jun)
    "8": "2-0",   # Australia 2-0 Turkiye (13 Jun)
    "9": "7-1",   # Germany 7-1 Curacao (14 Jun)
    "10": "2-2",  # Netherlands 2-2 Japan (14 Jun)
    "11": "1-0",  # Ivory Coast 1-0 Ecuador (14 Jun)
    "12": "5-1",  # Sweden 5-1 Tunisia (14 Jun)
    # Matchdays 13-24: no jugados aún (a partir de 15 Jun)
}

# ===== 1. ACTUALIZAR results.json =====
def update_results_json():
    path = os.path.join(BASE_DIR, "data", "runtime", "results.json")
    data = {
        "last_updated": "2026-06-15",
        "results": REAL_RESULTS,
        "frozen_matches": {k: True for k in REAL_RESULTS},
        "news_adjustments": {
            "Neymar_OUT": {"team": "Brazil", "impact": 0.15, "confirmed": True},
            "Aguerd_OUT": {"team": "Morocco", "impact": 0.15, "confirmed": True},
            "Abde_OUT": {"team": "Morocco", "impact": 0.1, "confirmed": True},
            "Davies_OUT": {"team": "Canada", "impact": 0.15, "confirmed": True},
            "Simons_OUT": {"team": "Netherlands", "impact": 0.12, "confirmed": True},
            "Pedri_OUT": {"team": "Spain", "impact": 0.12, "confirmed": True},
            "Rodrygo_OUT": {"team": "Brazil", "impact": 0.2, "confirmed": True}
        },
        "notes": [
            "Resultados REALES Fecha 1 Mundial 2026 (verificados web: FIFA, Olympics.com, MARCA):",
            "11 Jun: Mexico 2-0 South Africa ✅ | South Korea 2-1 Czechia ✅",
            "12 Jun: Canada 1-1 Bosnia ✅ | USA 4-1 Paraguay ✅",
            "13 Jun: Qatar 1-1 Switzerland ✅ | Brazil 1-1 Morocco ✅ | Haiti 0-1 Scotland ✅ | Australia 2-0 Turkiye ✅",
            "14 Jun: Germany 7-1 Curacao ✅ | Netherlands 2-2 Japan ✅ | Ivory Coast 1-0 Ecuador ✅ | Sweden 5-1 Tunisia ✅",
            "NOTA: FECHA1_RESULTADOS.md tenia 10/12 resultados inventados. Corregido con datos reales.",
            "Partidos 13-72: PENDIENTES (proximos dias)"
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [OK] results.json actualizado con {len(REAL_RESULTS)} resultados reales")

# ===== 2. FUNCIONES DE EVALUACION =====
def parse_js_object(text):
    result = {}
    if not text: return result
    text = text.strip().strip('{}').strip()
    if not text: return result
    for pair in re.findall(r'(\d+)\s*:\s*"([^"]*)"', text):
        result[int(pair[0])] = pair[1]
    return result


def parse_score(s):
    if not s or s == '-' or '-' not in str(s):
        return None
    parts = str(s).split('-')
    if len(parts) != 2:
        return None
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return None

def outcome(ga, gb):
    if ga > gb: return 'A'
    if ga < gb: return 'B'
    return 'D'

def evaluate(real, pred):
    if not real or not pred:
        return None
    r = parse_score(real)
    p = parse_score(pred)
    if not r or not p:
        return None
    if r[0] == p[0] and r[1] == p[1]:
        return 'exact'
    ro = outcome(r[0], r[1])
    po = outcome(p[0], p[1])
    return 'winner' if ro == po else 'wrong'

# ===== 3. ACTUALIZAR prode-mundial-2026.html =====
def update_html():
    path = os.path.join(BASE_DIR, "prode-mundial-2026.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Extraer matches array
    match_pattern = re.compile(r'const matches = \[(.*?)\];', re.DOTALL)
    match_match = match_pattern.search(html)
    if not match_match:
        print("  [ERR] No se pudo encontrar matches array")
        return
    matches_text = match_match.group(1)
    
    # Parse matches
    matches = []
    obj_pattern = re.compile(r'\{([^}]+)\}')
    for m in obj_pattern.finditer(matches_text):
        obj_text = m.group(1)
        obj = {}
        for part in obj_text.strip().split(','):
            part = part.strip()
            if ':' in part:
                key, val = part.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                obj[key] = val
        if obj.get('id'):
            matches.append(obj)
    
    print(f"  [DATA] {len(matches)} partidos parseados del HTML")
    
    # Extraer Oloraculo y Engine predictions
    ol_match = re.search(r'const OLORACULO_PREDS\s*=\s*(\{[^}]+\})', html)
    en_match = re.search(r'const ENGINE_PREDS\s*=\s*(\{[^}]+\})', html)
    
    oloraculo_preds = {}
    engine_preds = {}
    
    if ol_match:
        oloraculo_preds = parse_js_object(ol_match.group(1))
    
    if en_match:
        try:
            engine_preds = json.loads(en_match.group(1))
        except:
            engine_preds = {}
    
    # Keys de fuentes
    source_keys = ['c','g','f','fs','esp','yh','tips','e','cup','pm']
    source_labels = {
        'c':'Cascade','g':'ChatGPT','f':'Gemini','fs':'Fansided',
        'esp':'ESPN','yh':'Yahoo','tips':'1960Tips','e':'ELO',
        'cup':'Cup26','pm':'Polymarket','ol':'Oloráculo','en':'Engine'
    }
    
    # Calcular accuracy por fuente
    stats = {k: {'exact':0, 'winner':0, 'wrong':0, 'total':0} for k in source_keys + ['ol','en']}
    
    played_ids = [int(k) for k in REAL_RESULTS]
    played_ids_12 = [i for i in played_ids if i <= 12]
    
    for m in matches:
        mid = int(m.get('id', 0))
        if mid not in played_ids_12:
            continue
        real = REAL_RESULTS.get(str(mid))
        if not real:
            continue
        for sk in source_keys:
            pred = m.get(sk, '')
            e = evaluate(real, pred)
            if e == 'exact':
                stats[sk]['exact'] += 1
                stats[sk]['winner'] += 1
            elif e == 'winner':
                stats[sk]['winner'] += 1
            else:
                stats[sk]['wrong'] += 1
            stats[sk]['total'] += 1
        # Oloraculo
        ol_pred = str(oloraculo_preds.get(mid, ''))
        e = evaluate(real, ol_pred)
        if e == 'exact':
            stats['ol']['exact'] += 1
            stats['ol']['winner'] += 1
        elif e == 'winner':
            stats['ol']['winner'] += 1
        else:
            stats['ol']['wrong'] += 1
        stats['ol']['total'] += 1
        # Engine
        en_pred = str(engine_preds.get(str(mid), ''))
        e = evaluate(real, en_pred)
        if e == 'exact':
            stats['en']['exact'] += 1
            stats['en']['winner'] += 1
        elif e == 'winner':
            stats['en']['winner'] += 1
        else:
            stats['en']['wrong'] += 1
        stats['en']['total'] += 1
    
    # Source weights recalculation
    total_weight = 0
    weights = {}
    
    for sk in source_keys + ['ol', 'en']:
        s = stats[sk]
        if s['total'] > 0:
            exact_pct = (s['exact'] / s['total']) * 100
            winner_pct = (s['winner'] / s['total']) * 100
            conf_index = 0.3 * exact_pct + 0.7 * winner_pct
            confidence_weighted = conf_index
            # Recalcular peso: base 1.5, ajustado por confianza
            # Normalizar: conf_index 0-100 -> weight 0.5-2.5
            raw_weight = 0.5 + (conf_index / 100) * 2.0
            # Penalizar si muy pocas muestras
            sample_factor = min(s['total'] / 8.0, 1.0)
            raw_weight = 0.5 + (raw_weight - 0.5) * sample_factor
            raw_weight = max(0.5, min(2.5, raw_weight))
        else:
            exact_pct = 0
            winner_pct = 0
            conf_index = 0
            confidence_weighted = 0
            raw_weight = 1.0
        
        weights[sk] = round(raw_weight, 2)
        total_weight += raw_weight
    
    print(f"\n  [DATA] ACCURACY RECALCULADA ({len(played_ids_12)} partidos):")
    print(f"  {'Fuente':<12} {'Exacta':<8} {'Ganador':<8} {'Wrong':<8} {'Conf':<8} {'Peso':<8}")
    print(f"  {'-'*52}")
    sorted_sources = sorted(source_keys + ['ol', 'en'], key=lambda k: -(stats[k]['exact'] * 3 + stats[k]['winner']))
    for sk in sorted_sources:
        s = stats[sk]
        exact_pct = (s['exact']/s['total']*100) if s['total'] > 0 else 0
        winner_pct = (s['winner']/s['total']*100) if s['total'] > 0 else 0
        conf = 0.3 * exact_pct + 0.7 * winner_pct
        print(f"  {source_labels[sk]:<12} {exact_pct:>5.1f}%   {winner_pct:>5.1f}%   {s['wrong']:>3}    {conf:>5.1f}%   {weights[sk]:>5.2f}")
    
    # ===== ACTUALIZAR EMBEDDED_REAL_SCORES =====
    new_scores_json = json.dumps(REAL_RESULTS, ensure_ascii=False)
    html = re.sub(
        r'const EMBEDDED_REAL_SCORES\s*=\s*\{[^}]+\}',
        f'const EMBEDDED_REAL_SCORES = {new_scores_json}',
        html
    )
    print(f"  [OK] EMBEDDED_REAL_SCORES actualizado: {len(REAL_RESULTS)} scores")
    
    # ===== ACTUALIZAR ACCURACY_DATA =====
    accuracy_sources = {}
    for sk in source_keys + ['ol', 'en']:
        s = stats[sk]
        total = max(s['total'], 1)
        exact_pct = round((s['exact'] / total) * 100, 1)
        winner_pct = round((s['winner'] / total) * 100, 1)
        conf_idx = round(0.3 * exact_pct + 0.7 * winner_pct, 1)
        accuracy_sources[sk] = {
            "label": source_labels[sk],
            "exact_accuracy": exact_pct,
            "winner_accuracy": winner_pct,
            "confidence_index": conf_idx,
            "confidence_weighted": conf_idx,
            "samples": s['total'],
            "exact_hits": s['exact'],
            "winner_hits": s['winner'],
            "current_weight": weights[sk]
        }
    
    accuracy_data = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "matches_analyzed": len(played_ids_12),
        "sources": accuracy_sources,
        "real_results_verified": True,
        "note": "Resultados reales verificados de FIFA.com, Olympics.com, MARCA, NBC Sports"
    }
    accuracy_json = json.dumps(accuracy_data, ensure_ascii=False)
    
    # Reemplazar ACCURACY_DATA (buscar declaracion completa hasta el ;)
    acc_start = html.find('const ACCURACY_DATA = ')
    if acc_start >= 0:
        semi_pos = html.find(';', acc_start)
        if semi_pos > 0:
            old_text = html[acc_start:semi_pos+1]
            new_text = f'const ACCURACY_DATA = {accuracy_json};'
            html = html.replace(old_text, new_text)
            print(f"  [OK] ACCURACY_DATA actualizado ({len(old_text)} chars -> {len(new_text)} chars)")
        else:
            print("  [WARN] No se encontro ';' para ACCURACY_DATA")
    else:
        print("  [WARN] No se encontro 'const ACCURACY_DATA'")
    
    # ===== ACTUALIZAR SOURCE_WEIGHTS =====
    weight_entries = []
    for sk in source_keys:
        weight_entries.append(f"{sk}:{weights[sk]}")
    weight_entries.append(f"ol:{weights.get('ol', 0)}")
    weight_entries.append(f"en:{weights.get('en', 1.0)}")
    
    new_weights_str = '{' + ','.join(w for w in [f'{sk}:{weights[sk]}' for sk in source_keys] + [f'ol:{weights.get("ol", 0.0)}', f'en:{weights.get("en", 1.0)}']) + '}'
    new_total = sum(weights[sk] for sk in source_keys) + weights.get('ol', 0) + weights.get('en', 1.0)
    
    html = re.sub(
        r'const SOURCE_WEIGHTS\s*=\s*\{[^}]+\}',
        f'const SOURCE_WEIGHTS = {new_weights_str}',
        html
    )
    html = re.sub(
        r'const TOTAL_WEIGHT\s*=\s*[\d.]+',
        f'const TOTAL_WEIGHT = {round(new_total, 2)}',
        html
    )
    print(f"  [OK] SOURCE_WEIGHTS recalculados (total={round(new_total, 2)})")
    
    # ===== ACTUALIZAR METADATA EN HEADER =====
    today_str = "15 Jun 2026"
    html = re.sub(
        r'Actualizado \d+ \w+ \d+ · \d+:\d+ \w+ · \d+ partidos jugados',
        f'Actualizado {today_str} · 19:00 AR · {len(played_ids_12)} partidos jugados',
        html
    )
    print(f"  [OK] Header metadata actualizado: {len(played_ids_12)} partidos jugados")
    
    # ===== ACTUALIZAR STANDINGS EN DYNAMIC_PREDICTIONS =====
    # Standings reales calculados de los resultados
    standings = {}
    
    def update_standings(group, team, gf, ga, is_home):
        if group not in standings:
            standings[group] = {}
        if team not in standings[group]:
            standings[group][team] = {'played': 0, 'points': 0, 'gf': 0, 'ga': 0, 'gd': 0}
        standings[group][team]['played'] += 1
        standings[group][team]['gf'] += gf
        standings[group][team]['ga'] += ga
        standings[group][team]['gd'] = standings[group][team]['gf'] - standings[group][team]['ga']
        if gf > ga:
            standings[group][team]['points'] += 3
        elif gf == ga:
            standings[group][team]['points'] += 1
    
    # Mapeo de matches a grupos (del HTML)
    match_groups = {}
    for m in matches:
        mid = int(m['id'])
        match_groups[mid] = {'gr': m.get('gr',''), 'a': m.get('a',''), 'b': m.get('b','')}
    
    for mid_str, score_str in REAL_RESULTS.items():
        mid = int(mid_str)
        if mid not in match_groups:
            continue
        mg = match_groups[mid]
        gf_a, gf_b = parse_score(score_str)
        if gf_a is None:
            continue
        gr = mg['gr']
        home_team = mg['a']
        away_team = mg['b']
        update_standings(gr, home_team, gf_a, gf_b, True)
        update_standings(gr, away_team, gf_b, gf_a, False)
    
    # Add placeholder standings for groups with no matches yet
    all_groups = ['A','B','C','D','E','F','G','H','I','J','K','L']
    for g in all_groups:
        if g not in standings:
            standings[g] = {}
    
    # Check if DYNAMIC_PREDICTIONS exists and update standings
    dp_match = re.search(r'const DYNAMIC_PREDICTIONS\s*=\s*(\{.*?"standings"\s*:\s*\{)', html, re.DOTALL)
    if dp_match:
        # Reemplazar solo la sección de standings dentro de DYNAMIC_PREDICTIONS
        # Primero, encontrar el JSON completo de DYNAMIC_PREDICTIONS para extraer metadata
        dp_full_match = re.search(r'const DYNAMIC_PREDICTIONS\s*=\s*(\{.+"standings"\s*:\s*\{)(.+?)(\})\s*;', html, re.DOTALL)
        if dp_full_match:
            prefix = dp_full_match.group(1)
            rest = dp_full_match.group(3)
            # Buscar el final del objeto standings (encontrar el matching })
            # Reemplazar con standings reales y preservar el resto
            # Estrategia: reconstruir el JSON completo
            dp_obj_text = dp_full_match.group(0)
            # Simplemente reemplazar las standings en el DYNAMIC_PREDICTIONS
            old_standings_match = re.search(r'"standings"\s*:\s*\{[^}]+\}(?=\s*,"[a-z])', dp_obj_text, re.DOTALL)
            if old_standings_match:
                new_standings_json = json.dumps(standings, ensure_ascii=False)
                dp_obj_text = dp_obj_text.replace(old_standings_match.group(0), f'"standings": {new_standings_json}')
                html = html.replace(dp_full_match.group(0), dp_obj_text)
                print(f"  [OK] Standings actualizados en DYNAMIC_PREDICTIONS")
    else:
        print(f"  [WARN] No se encontro DYNAMIC_PREDICTIONS para actualizar standings")
    
    # ===== ACTUALIZAR TAMBIÉN index.html con redirect final =====
    # No modificamos index.html - vercel.json ya redirige
    
    # ===== GUARDAR HTML =====
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  [OK] prode-mundial-2026.html guardado exitosamente")
    return accuracy_data, weights, stats


if __name__ == "__main__":
    print("ACTUALIZACION DE RESULTADOS REALES MUNDIAL 2026")
    print("=" * 60)
    print("Fuentes: FIFA.com, Olympics.com, MARCA, NBC Sports, Bundesliga, Daily Mirror")
    print()
    update_results_json()
    print()
    accuracy, weights, stats = update_html()
    print()
    print("=" * 60)
    print("ACTUALIZACION COMPLETA")
    print("   Resultados reales: 12 partidos")
    print("   FECHA1_RESULTADOS.md tenia 10/12 resultados inventados - CORREGIDO")
    print()
    print("PROXIMOS PARTIDOS:")
    print("   15 Jun: Spain vs Cape Verde, Belgium vs Egypt, Saudi Arabia vs Uruguay, Iran vs New Zealand")
    print("   16 Jun: France vs Senegal, Iraq vs Norway, Argentina vs Algeria, Austria vs Jordan")
    print("   17 Jun: Portugal vs DR Congo, England vs Croatia, Ghana vs Panama, Uzbekistan vs Colombia")
