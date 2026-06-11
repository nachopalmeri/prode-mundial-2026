#!/usr/bin/env python3
"""
Integrar Polymarket como fuente #10 en el HTML del Prode Mundial 2026
"""

import json
import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "..")

# Leer predicciones de Polymarket
polymarket_file = os.path.join(project_dir, "cup26-model", "data", "raw", "polymarket_predictions_20260611_1247.json")
with open(polymarket_file, 'r') as f:
    predictions_polymarket = json.load(f)

# Tomar solo los primeros 72 (del 1 al 72)
# Ya están en formato correcto

# Leer HTML
html_path = os.path.join(project_dir, "prode-mundial-2026.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Agregar campo 'pm' (Polymarket) a cada partido
for match_id, score in predictions_polymarket.items():
    if int(match_id) > 72:
        continue
    pattern = rf'({{id:{match_id},gr:"[A-Z]",d:"[^"]+",t:"[^"]+",a:"[^"]+",b:"[^"]+",c:"[^"]+",g:"[^"]+",f:"[^"]+",fs:"[^"]+",esp:"[^"]+",yh:"[^"]+",t:"[^"]+",e:"[^"]+",cup:"[^"]+")(,ch:)'
    replacement = rf'\1,pm:"{score}"\2'
    html = re.sub(pattern, replacement, html)

# 2. Actualizar getConsensus para 10 fuentes
html = html.replace(
    'function getConsensus(c,g,m,fs,esp,yh,t,e,cup){',
    'function getConsensus(c,g,m,fs,esp,yh,t,e,cup,pm){'
)
html = html.replace(
    'const scores=[c,g,m,fs,esp,yh,t,e,cup];',
    'const scores=[c,g,m,fs,esp,yh,t,e,cup,pm];'
)
html = html.replace(
    "const keys=['c','g','m','fs','esp','yh','t','e','cup'];",
    "const keys=['c','g','m','fs','esp','yh','t','e','cup','pm'];"
)
html = html.replace(
    'const SOURCE_WEIGHTS={c:1.0,g:1.0,m:1.0,fs:0.8,esp:1.3,yh:0.8,t:1.5,e:1.5,cup:1.4};',
    'const SOURCE_WEIGHTS={c:1.0,g:1.0,m:1.0,fs:0.8,esp:1.3,yh:0.8,t:1.5,e:1.5,cup:1.4,pm:1.6};'
)
html = html.replace(
    'const TOTAL_WEIGHT=10.3;',
    'const TOTAL_WEIGHT=11.9;'
)

# 3. Actualizar promedios para 10 fuentes
html = html.replace(
    'if(bestWeight>=TOTAL_WEIGHT*0.40)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'high\'};',
    'if(bestWeight>=TOTAL_WEIGHT*0.38)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'high\'};'
)
html = html.replace(
    'if(bestWeight>=TOTAL_WEIGHT*0.25)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'medium\'};',
    'if(bestWeight>=TOTAL_WEIGHT*0.22)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'medium\'};'
)

# 4. Actualizar getMatchPoints
html = html.replace(
    "source==='e'?m.e:source==='cup'?m.cup:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup).score;",
    "source==='e'?m.e:source==='cup'?m.cup:source==='pm'?m.pm:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup,m.pm).score;"
)

# 5. Actualizar updateScores
html = html.replace(
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,e=0,cup=0,f=0,played=0;',
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,e=0,cup=0,pm=0,f=0,played=0;'
)
html = html.replace(
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pe=getMatchPoints(x.id,'e'),pcup=getMatchPoints(x.id,'cup'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; e+=pe; cup+=pcup; f+=pf;",
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pmatch=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pe=getMatchPoints(x.id,'e'),pcup=getMatchPoints(x.id,'cup'),ppm=getMatchPoints(x.id,'pm'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pmatch; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; e+=pe; cup+=pcup; pm+=ppm; f+=pf;"
)
html = html.replace(
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-e-'+x.id,pe);setPts('pts-cup-'+x.id,pcup);setPts('pts-f-'+x.id,pf);",
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pmatch);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-e-'+x.id,pe);setPts('pts-cup-'+x.id,pcup);setPts('pts-pm-'+x.id,ppm);setPts('pts-f-'+x.id,pf);"
)

# 6. Agregar scoreboard item para Polymarket
html = html.replace(
    '<div class="score-item"><div class="score-label">Cup26 AI</div><div class="score-value" id="pts-cup26">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>',
    '<div class="score-item"><div class="score-label">Cup26 AI</div><div class="score-value" id="pts-cup26">0</div></div>\n<div class="score-item"><div class="score-label">Polymarket</div><div class="score-value" id="pts-polymarket">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>'
)

# 7. Actualizar scoreboard JS
html = html.replace(
    "document.getElementById('pts-cup26').textContent=cup;\n  document.getElementById('pts-consensus').textContent=f;",
    "document.getElementById('pts-cup26').textContent=cup;\n  document.getElementById('pts-polymarket').textContent=pm;\n  document.getElementById('pts-consensus').textContent=f;"
)

# 8. Actualizar tabla comparativa header
html = html.replace(
    '<th style="text-align:center">Cup26 AI</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">ELO</th><th style="text-align:center">Cup26</th><th style="text-align:center">Con</th>',
    '<th style="text-align:center">Cup26 AI</th>\n<th style="text-align:center">Polymarket</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">ELO</th><th style="text-align:center">Cup26</th><th style="text-align:center">Polym</th><th style="text-align:center">Con</th>'
)

# 9. Actualizar renderComparativa
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup)',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup,x.pm)'
)
html = html.replace(
    '${con.agree}/9</td>',
    '${con.agree}/10</td>'
)
html = html.replace(
    '<td style="text-align:center"><span class="pred pred-cascade" style="background:#ffedd5;color:#9a3412">${x.cup}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>',
    '<td style="text-align:center"><span class="pred pred-cascade" style="background:#ffedd5;color:#9a3412">${x.cup}</span></td>\n    <td style="text-align:center"><span class="pred pred-chatgpt" style="background:#dbeafe;color:#1e40af">${x.pm}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>'
)
html = html.replace(
    '<td style="text-align:center" id="pts-cup-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>',
    '<td style="text-align:center" id="pts-cup-${x.id}"></td>\n    <td style="text-align:center" id="pts-pm-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>'
)

# 10. Actualizar renderFinal y renderProde
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup);',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup,x.pm);'
)

# 11. Actualizar updateInputStyle y updateProde
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup,m.pm).score);'
)

# 12. Actualizar min-width de tabla
html = html.replace(
    'min-width:2100px',
    'min-width:2300px'
)

# 13. Actualizar texto de pestaña
html = html.replace(
    'Comparativa 9 IA',
    'Comparativa 10 IA'
)

# 14. Actualizar contador de fuentes en dashboard
html = html.replace(
    '<div class="stat-card"><div class="stat-value" id="stat-sources">9</div><div class="stat-label">Fuentes IA</div></div>',
    '<div class="stat-card"><div class="stat-value" id="stat-sources">10</div><div class="stat-label">Fuentes IA</div></div>'
)

# 15. Actualizar pesos en dashboard chart
html = html.replace(
    "labels:['Cascade','ChatGPT','Gemini','Fansided','ESPN','Yahoo','1960Tips','ELO','Cup26'],",
    "labels:['Cascade','ChatGPT','Gemini','Fansided','ESPN','Yahoo','1960Tips','ELO','Cup26','Polymkt'],"
)
html = html.replace(
    "data:[1.0,1.0,1.0,0.8,1.3,0.8,1.5,1.5,1.4]",
    "data:[1.0,1.0,1.0,0.8,1.3,0.8,1.5,1.5,1.4,1.6]"
)
html = html.replace(
    "backgroundColor:['#dbeafe','#f3e8ff','#d1fae5','#fef3c7','#fce7f3','#e0e7ff','#f3e8ff','#ccfbf1','#ffedd5']",
    "backgroundColor:['#dbeafe','#f3e8ff','#d1fae5','#fef3c7','#fce7f3','#e0e7ff','#f3e8ff','#ccfbf1','#ffedd5','#dbeafe']"
)

# Guardar HTML actualizado
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML actualizado con Polymarket como fuente #10")
print(f"Total de partidos actualizados: 72")
