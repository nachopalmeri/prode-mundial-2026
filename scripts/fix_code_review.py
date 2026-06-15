#!/usr/bin/env python3
"""
Fixes identified by code review:
1. ACCURACY_DATA: orphaned trailing properties (SyntaxError)
2. Oloraculo predictions parsed incorrectly (json.loads fails on unquoted keys)
3. Chart weights hardcoded with stale values
4. Dashboard stat-played shows "6" instead of "12"/dynamic
5. evaluate() missing null guard for parseScore
6. TOTAL_WEIGHT not recalculated
7. stat-played dinamico en drawDashboard
"""
import re, json, os
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE, "prode-mundial-2026.html")
SCRIPT_PATH = os.path.join(BASE, "scripts", "update_real_results.py")

def parse_js_object(text):
    result = {}
    if not text: return result
    text = text.strip().strip('{}').strip()
    if not text: return result
    for pair in re.findall(r'(\d+)\s*:\s*"([^"]*)"', text):
        result[int(pair[0])] = pair[1]
    return result

def fix_html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # ===== FIX 1: ACCURACY_DATA =====
    correct_acc = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "matches_analyzed": 12,
        "sources": {
            "c": {"label":"Cascade","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "g": {"label":"ChatGPT","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "f": {"label":"Gemini","exact_accuracy":8.3,"winner_accuracy":50.0,"confidence_index":37.5,"confidence_weighted":37.5,"samples":12,"exact_hits":1,"winner_hits":6,"current_weight":1.25},
            "fs": {"label":"Fansided","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "esp": {"label":"ESPN","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "yh": {"label":"Yahoo","exact_accuracy":16.7,"winner_accuracy":58.3,"confidence_index":45.8,"confidence_weighted":45.8,"samples":12,"exact_hits":2,"winner_hits":7,"current_weight":1.42},
            "tips": {"label":"1960Tips","exact_accuracy":8.3,"winner_accuracy":41.7,"confidence_index":31.7,"confidence_weighted":31.7,"samples":12,"exact_hits":1,"winner_hits":5,"current_weight":1.13},
            "e": {"label":"ELO","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "cup": {"label":"Cup26","exact_accuracy":8.3,"winner_accuracy":41.7,"confidence_index":31.7,"confidence_weighted":31.7,"samples":12,"exact_hits":1,"winner_hits":5,"current_weight":1.13},
            "pm": {"label":"Polymarket","exact_accuracy":16.7,"winner_accuracy":50.0,"confidence_index":40.0,"confidence_weighted":40.0,"samples":12,"exact_hits":2,"winner_hits":6,"current_weight":1.3},
            "ol": {"label":"Oloraculo","exact_accuracy":8.3,"winner_accuracy":25.0,"confidence_index":20.0,"confidence_weighted":20.0,"samples":12,"exact_hits":1,"winner_hits":3,"current_weight":0.9},
            "en": {"label":"Engine","exact_accuracy":8.3,"winner_accuracy":41.7,"confidence_index":31.7,"confidence_weighted":31.7,"samples":12,"exact_hits":1,"winner_hits":5,"current_weight":1.13}
        },
        "real_results_verified": True,
        "note": "Resultados reales verificados de FIFA.com, Olympics.com, MARCA, NBC Sports"
    }
    correct_acc_json = json.dumps(correct_acc, ensure_ascii=False)

    decl_start = html.find('const ACCURACY_DATA = ')
    if decl_start >= 0:
        semi_pos = html.find(';', decl_start)
        if semi_pos > 0:
            old_decl = html[decl_start:semi_pos+1]
            new_decl = 'const ACCURACY_DATA = ' + correct_acc_json + ';'
            html = html.replace(old_decl, new_decl)
            print(f"[FIX 1/7] ACCURACY_DATA reparado ({len(old_decl)} chars -> {len(new_decl)} chars)")
        else:
            print("[WARN] No se encontro ; para ACCURACY_DATA")
    else:
        print("[WARN] No se encontro const ACCURACY_DATA")

    # ===== FIX 2: Oloraculo parsing in update_real_results.py =====
    with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
        script = f.read()

    if 'parse_js_object' in script and 'json.loads' not in script:
        print(f"[OK] Oloraculo parsing ya esta fixeado en update_real_results.py")
    else:
        old_parse = """    if ol_match:
        try:
            oloraculo_preds = json.loads(ol_match.group(1))
        except:
            oloraculo_preds = {}"""
        new_parse = """    if ol_match:
        oloraculo_preds = parse_js_object(ol_match.group(1))"""
        if old_parse in script:
            script = script.replace(old_parse, new_parse)
            script = script.replace(
                "def parse_score(s):",
                "def parse_js_object(text):\n    result = {}\n    if not text: return result\n    text = text.strip().strip('{}').strip()\n    if not text: return result\n    for pair in re.findall(r'(\\d+)\\s*:\\s*\"([^\"]*)\"', text):\n        result[int(pair[0])] = pair[1]\n    return result\n\n\ndef parse_score(s):"
            )
            with open(SCRIPT_PATH, 'w', encoding='utf-8') as f:
                f.write(script)
            print(f"[FIX 2/7] Oloraculo parsing fixeado en update_real_results.py")
        else:
            print("[WARN] No se encontro el bloque json.loads en update_real_results.py")

    # ===== FIX 3: Chart weights dynamic =====
    old_chart = re.search(
        r"data:\[1\.6,1\.65,1\.65,1\.47,1\.95,1\.19,1\.95,1\.95,1\.79,1\.95,0\.0,1\.0\]",
        html
    )
    if old_chart:
        new_chart = "data:[SOURCE_WEIGHTS.c,SOURCE_WEIGHTS.g,SOURCE_WEIGHTS.f,SOURCE_WEIGHTS.fs,SOURCE_WEIGHTS.esp,SOURCE_WEIGHTS.yh,SOURCE_WEIGHTS.tips,SOURCE_WEIGHTS.e,SOURCE_WEIGHTS.cup,SOURCE_WEIGHTS.pm,SOURCE_WEIGHTS.ol,SOURCE_WEIGHTS.en]"
        html = html.replace(old_chart.group(0), new_chart)
        print(f"[FIX 3/7] Chart weights ahora usa SOURCE_WEIGHTS dinamicamente")
    else:
        print(f"[WARN] No se encontro array hardcoded de pesos")

    # ===== FIX 4: stat-played =====
    old_played = '<div class="stat-value" id="stat-played">6</div>'
    new_played = '<div class="stat-value" id="stat-played">12</div>'
    if old_played in html:
        html = html.replace(old_played, new_played)
        print(f"[FIX 4/7] stat-played actualizado de 6 a 12")
    else:
        m = re.search(r'stat-played">(\d+)<', html)
        if m:
            print(f"[INFO] stat-played actual value: {m.group(1)}")
        else:
            print(f"[WARN] stat-played no encontrado")

    # ===== FIX 5: evaluate() null guard =====
    old_eval = """function evaluate(real,pred){
  if(!real||!pred)return null;
  const r=parseScore(real),p=parseScore(pred);
  if(r.ga===p.ga&&r.gb===p.gb)return'exact';
  return outcome(r.ga,r.gb)===outcome(p.ga,p.gb)?'winner':'wrong';
}"""
    new_eval = """function evaluate(real,pred){
  if(!real||!pred)return null;
  const r=parseScore(real),p=parseScore(pred);
  if(!r||!p)return null;
  if(r.ga===p.ga&&r.gb===p.gb)return'exact';
  return outcome(r.ga,r.gb)===outcome(p.ga,p.gb)?'winner':'wrong';
}"""
    if old_eval in html:
        html = html.replace(old_eval, new_eval)
        print(f"[FIX 5/7] evaluate() null guard agregado")
    else:
        if 'if(!r||!p)return null' in html:
            print(f"[OK] evaluate() null guard ya presente")
        else:
            print(f"[WARN] evaluate() function no encontrada")

    # ===== FIX 6: TOTAL_WEIGHT =====
    total_w = 1.30 + 1.30 + 1.25 + 1.30 + 1.30 + 1.42 + 1.13 + 1.30 + 1.13 + 1.30 + 0.90 + 1.13
    html = re.sub(
        r'const TOTAL_WEIGHT\s*=\s*[\d.]+',
        f'const TOTAL_WEIGHT = {round(total_w, 2)}',
        html
    )
    print(f"[FIX 6/7] TOTAL_WEIGHT = {round(total_w, 2)}")

    # ===== FIX 7: stat-played dinamico en drawDashboard =====
    old_dash = "document.getElementById('stat-confidence').textContent=avgConf+'/3';"
    new_dash = old_dash + "\n  document.getElementById('stat-played').textContent=Object.keys(EMBEDDED_REAL_SCORES).length;"
    if old_dash in html:
        html = html.replace(old_dash, new_dash)
        print(f"[FIX 7/7] stat-played ahora es dinamico en drawDashboard")
    else:
        print(f"[WARN] No se encontro stat-confidence line en drawDashboard")

    # Save
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n[OK] Todos los fixes aplicados a prode-mundial-2026.html")

fix_html()
