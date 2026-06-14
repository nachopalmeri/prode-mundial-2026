#!/usr/bin/env python3
"""
Update prode-mundial-2026.html with 12th source: Engine (Poisson+Dixon-Coles).
Reads engine_predictions.json and patches the HTML.
"""
import json, re, os

HTML_PATH = os.path.join(os.path.dirname(__file__), '..', 'prode-mundial-2026.html')
ENGINE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'runtime', 'engine_predictions.json')

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

with open(ENGINE_PATH, 'r', encoding='utf-8') as f:
    engine_data = json.load(f)

# Extract engine predictions (combined model)
engine_preds = engine_data['engine']
elo_preds = engine_data['elo']
poisson_preds = engine_data['poisson']

# Build ENGINE_PREDS scoreline object
engine_scorelines = {}
for match_id in sorted(engine_preds.keys(), key=int):
    engine_scorelines[int(match_id)] = engine_preds[match_id]['scoreline']

changes = 0

# 1. Update SOURCE_KEYS
old = "const SOURCE_KEYS = ['c','g','f','fs','esp','yh','tips','e','cup','pm','ol'];"
new = "const SOURCE_KEYS = ['c','g','f','fs','esp','yh','tips','e','cup','pm','ol','en'];"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated SOURCE_KEYS")
else:
    print("WARN: SOURCE_KEYS not found")

# 2. Update SOURCE_LABELS
old = "const SOURCE_LABELS = {c:'Cascade',g:'ChatGPT',f:'Gemini',fs:'Fansided',esp:'ESPN',yh:'Yahoo',tips:'1960Tips',e:'ELO',cup:'Cup26',pm:'Polymarket',ol:'Olor\u00e1culo'};"
new = "const SOURCE_LABELS = {c:'Cascade',g:'ChatGPT',f:'Gemini',fs:'Fansided',esp:'ESPN',yh:'Yahoo',tips:'1960Tips',e:'ELO',cup:'Cup26',pm:'Polymarket',ol:'Olor\u00e1culo',en:'Engine'};"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated SOURCE_LABELS")
else:
    # Try with plain "Oloráculo"
    old2 = "const SOURCE_LABELS = {c:'Cascade',g:'ChatGPT',f:'Gemini',fs:'Fansided',esp:'ESPN',yh:'Yahoo',tips:'1960Tips',e:'ELO',cup:'Cup26',pm:'Polymarket',ol:'Olor\u00e1culo'};"
    if old2 in html:
        html = html.replace(old2, new)
        changes += 1
        print("Updated SOURCE_LABELS")
    else:
        print("WARN: SOURCE_LABELS not found")

# 3. Update SOURCE_COLORS
old = "const SOURCE_COLORS = {c:'pred-cascade',g:'pred-chatgpt',f:'pred-gemini',fs:'pred-fansided',esp:'pred-espn',yh:'pred-yahoo',tips:'pred-1960tips',e:'pred-elo',cup:'pred-cup26',pm:'pred-polymarket'};"
new = "const SOURCE_COLORS = {c:'pred-cascade',g:'pred-chatgpt',f:'pred-gemini',fs:'pred-fansided',esp:'pred-espn',yh:'pred-yahoo',tips:'pred-1960tips',e:'pred-elo',cup:'pred-cup26',pm:'pred-polymarket',ol:'pred-oloraculo',en:'pred-engine'};"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated SOURCE_COLORS")
else:
    print("WARN: SOURCE_COLORS not found")

# 4. Update SOURCE_WEIGHTS
old = "const SOURCE_WEIGHTS = {c:1.6, cup:1.79, e:1.95, esp:1.95, f:1.65, fs:1.47, g:1.65, pm:1.95, tips:1.95, yh:1.19, ol:3.0};"
new = "const SOURCE_WEIGHTS = {c:1.6, cup:1.79, e:1.95, esp:1.95, f:1.65, fs:1.47, g:1.65, pm:1.95, tips:1.95, yh:1.19, ol:3.0, en:1.5};"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated SOURCE_WEIGHTS")
else:
    print("WARN: SOURCE_WEIGHTS not found")

# 5. Update TOTAL_WEIGHT
old = "const TOTAL_WEIGHT = 20.15;"
new = "const TOTAL_WEIGHT = 23.15;"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated TOTAL_WEIGHT")
else:
    print("WARN: TOTAL_WEIGHT not found")

# 6. Add ENGINE_PREDS after OLORACULO_PREDS
old = """const OLORACULO_PREDS = {1:"1-0",2:"1-1",3:"1-0",4:"1-1",5:"1-2",6:"1-1",7:"1-1",8:"1-1",9:"2-0",10:"1-1",11:"0-0",12:"1-1",13:"2-0",14:"1-0",15:"0-1",16:"1-1",17:"1-1",18:"0-1",19:"1-1",20:"1-1",21:"1-0",22:"1-1",23:"1-1",24:"1-1",25:"1-1",26:"2-0",27:"1-0",28:"1-1",29:"1-1",30:"1-1",31:"2-0",32:"1-1",33:"2-1",34:"1-1",35:"1-0",36:"0-1",37:"1-0",38:"1-1",39:"1-0",40:"1-1",41:"1-1",42:"1-0",43:"1-1",44:"1-1",45:"1-1",46:"2-0",47:"1-1",48:"1-0",49:"1-1",50:"1-1",51:"1-1",52:"1-1",53:"1-1",54:"0-1",55:"1-1",56:"0-1",57:"2-1",58:"0-1",59:"1-1",60:"0-1",61:"1-1",62:"1-0",63:"0-1",64:"1-1",65:"0-1",66:"1-1",67:"0-2",68:"1-0",69:"1-1",70:"0-0",71:"1-1",72:"0-2"};"""

engine_json_str = json.dumps(engine_scorelines)
new = f"const OLORACULO_PREDS = {engine_json_str};\nconst ENGINE_PREDS = {engine_json_str};"
# Actually use the original OLORACULO_PREDS since the engine makes slightly different predictions
# Let me keep OLORACULO_PREDS as-is and add ENGINE_PREDS after it
new_with_engine = old + f"\nconst ENGINE_PREDS = {json.dumps(engine_scorelines)};"

if old in html:
    html = html.replace(old, new_with_engine)
    changes += 1
    print("Added ENGINE_PREDS")
else:
    print("WARN: OLORACULO_PREDS not found for ENGINE_PREDS insertion")

# 7. Update sourceDistribution to include ENGINE_PREDS
old = "const scores=[matchObj.c,matchObj.g,matchObj.f,matchObj.fs,matchObj.esp,matchObj.yh,matchObj.tips,matchObj.e,matchObj.cup,matchObj.pm,OLORACULO_PREDS[matchObj.id]||'-'];"
new = "const scores=[matchObj.c,matchObj.g,matchObj.f,matchObj.fs,matchObj.esp,matchObj.yh,matchObj.tips,matchObj.e,matchObj.cup,matchObj.pm,OLORACULO_PREDS[matchObj.id]||'-',ENGINE_PREDS[matchObj.id]||'-'];"
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated sourceDistribution")
else:
    print("WARN: sourceDistribution not found")

# 8. Update DYNAMIC_PREDICTIONS metadata source_count
old = '"source_count":11'
new = '"source_count":12'
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated DYNAMIC_PREDICTIONS source_count")
else:
    print("WARN: DYNAMIC_PREDICTIONS source_count not found")

# 9. Update meta description and OG tags (11 -> 12)
for x in range(3):
    old = '11 fuentes IA'
    new = '12 fuentes IA'
    if old in html:
        html = html.replace(old, new)
        changes += 1
        print(f"Updated meta: {old} -> {new}")
    else:
        print("WARN: meta '11 fuentes IA' not found")
        break

# 10. Update subtitle "11 Fuentes" to "12 Fuentes"
old = 'Comparador de Predicciones &middot; 11 Fuentes'
new = 'Comparador de Predicciones &middot; 12 Fuentes'
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated subtitle 11->12 Fuentes")
else:
    # Try another format
    old2 = 'Comparador de Predicciones \u00b7 11 Fuentes'
    new2 = 'Comparador de Predicciones \u00b7 12 Fuentes'
    if old2 in html:
        html = html.replace(old2, new2)
        changes += 1
        print("Updated subtitle 11->12 Fuentes (unicode)")
    else:
        print("WARN: subtitle '11 Fuentes' not found")

# 11. Update card-sub "11 Fuentes IA"
old = 'card-sub">11 Fuentes IA'
new = 'card-sub">12 Fuentes IA'
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated card-sub 11->12 Fuentes IA")
else:
    print("WARN: card-sub 11 Fuentes IA not found")

# 12. Update stat-sources value
old = 'id="stat-sources">11<'
new = 'id="stat-sources">12<'
if old in html:
    html = html.replace(old, new)
    changes += 1
    print("Updated stat-sources 11->12")
else:
    print("WARN: stat-sources not found")

# 13. Add engine accuracy data if present
# Read the engine's accuracy (we'll compute 0 for now since no real results yet)
engine_accuracy_entry = '''
    "en": {"label": "Engine", "exact_accuracy": 0.0, "winner_accuracy": 0.0, "confidence_index": 0.0, "confidence_weighted": 0.0, "samples": 0, "exact_hits": 0, "winner_hits": 0, "current_weight": 1.5},'''

# Add after oloraculo in ACCURACY_DATA.sources
old = '    "ol": {"label": "Olor\u00e1culo", "exact_accuracy": 0.0, "winner_accuracy": 0.0, "confidence_index": 0.0, "confidence_weighted": 0.0, "samples": 0, "exact_hits": 0, "winner_hits": 0, "current_weight": 3.0}'
new_ol = old.rstrip(',') + ','
if old in html:
    html = html.replace(old, new_ol + '\n    "en": {"label": "Engine", "exact_accuracy": 0.0, "winner_accuracy": 0.0, "confidence_index": 0.0, "confidence_weighted": 0.0, "samples": 0, "exact_hits": 0, "winner_hits": 0, "current_weight": 1.5}')
    changes += 1
    print("Updated ACCURACY_DATA for Engine")
else:
    print("WARN: ACCURACY_DATA ol not found")

# 14. Add CSS for pred-engine color
old_css = ".pred-oloraculo{background:#8b5cf6;color:#fff}"
new_css = ".pred-oloraculo{background:#8b5cf6;color:#fff}\n.pred-engine{background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff}"
if old_css in html:
    html = html.replace(old_css, new_css)
    changes += 1
    print("Added pred-engine CSS")
else:
    print("WARN: pred-oloraculo CSS not found")

# Write back
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n=== Done: {changes} changes made ===")
