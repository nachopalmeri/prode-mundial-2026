#!/usr/bin/env python3
"""
Script para agregar predicciones de Cup26 AI (modelo Elo + Dixon-Coles + Monte Carlo)
al HTML del Prode Mundial 2026.
"""

import json
import re

# Leer predicciones de Cup26
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'cup26-model', 'predictions_cup26.json'), 'r') as f:
    predictions_cup26 = json.load(f)

# Completar partidos faltantes basados en consenso de otras fuentes
missing = {
    "12": "2-0",  # Sweden vs Tunisia - consenso
    "33": "2-1",  # Germany vs Ivory Coast - consenso
    "53": "2-1"   # Japan vs Sweden - consenso
}
predictions_cup26.update(missing)

# Leer el HTML actual
html_path = os.path.join(script_dir, 'prode-mundial-2026.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Actualizar los datos de los partidos para incluir Cup26 (campo 'cup')
for match_id, score in predictions_cup26.items():
    pattern = rf'({{id:{match_id},gr:"[A-Z]",d:"[^"]+",t:"[^"]+",a:"[^"]+",b:"[^"]+",c:"[^"]+",g:"[^"]+",f:"[^"]+",fs:"[^"]+",esp:"[^"]+",yh:"[^"]+",t:"[^"]+",e:"[^"]+")(,ch:)'
    replacement = rf'\1,cup:"{score}"\2'
    html = re.sub(pattern, replacement, html)

# Actualizar getConsensus para 9 fuentes
html = html.replace(
    'function getConsensus(c,g,m,fs,esp,yh,t,e){',
    'function getConsensus(c,g,m,fs,esp,yh,t,e,cup){'
)
html = html.replace(
    'const scores=[c,g,m,fs,esp,yh,t,e];',
    'const scores=[c,g,m,fs,esp,yh,t,e,cup];'
)
html = html.replace(
    "const keys=['c','g','m','fs','esp','yh','t','e'];",
    "const keys=['c','g','m','fs','esp','yh','t','e','cup'];"
)
html = html.replace(
    'const SOURCE_WEIGHTS={c:1.0,g:1.0,m:1.0,fs:0.8,esp:1.3,yh:0.8,t:1.5,e:1.5};',
    'const SOURCE_WEIGHTS={c:1.0,g:1.0,m:1.0,fs:0.8,esp:1.3,yh:0.8,t:1.5,e:1.5,cup:1.4};'
)
html = html.replace(
    'const TOTAL_WEIGHT=8.9;',
    'const TOTAL_WEIGHT=10.3;'
)

# Actualizar promedios
html = html.replace(
    'if(bestWeight>=TOTAL_WEIGHT*0.45)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'high\'};',
    'if(bestWeight>=TOTAL_WEIGHT*0.40)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'high\'};'
)
html = html.replace(
    'if(bestWeight>=TOTAL_WEIGHT*0.30)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'medium\'};',
    'if(bestWeight>=TOTAL_WEIGHT*0.25)return{score:bestScore,agree:Math.round(bestWeight),confidence:\'medium\'};'
)

# Actualizar getMatchPoints para incluir 'cup'
html = html.replace(
    "source==='e'?m.e:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score;",
    "source==='e'?m.e:source==='cup'?m.cup:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup).score;"
)

# Actualizar updateScores para incluir Cup26
html = html.replace(
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,e=0,f=0,played=0;',
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,e=0,cup=0,f=0,played=0;'
)
html = html.replace(
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pe=getMatchPoints(x.id,'e'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; e+=pe; f+=pf;",
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pe=getMatchPoints(x.id,'e'),pcup=getMatchPoints(x.id,'cup'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; e+=pe; cup+=pcup; f+=pf;"
)
html = html.replace(
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-e-'+x.id,pe);setPts('pts-f-'+x.id,pf);",
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-e-'+x.id,pe);setPts('pts-cup-'+x.id,pcup);setPts('pts-f-'+x.id,pf);"
)

# Agregar scoreboard item para Cup26
html = html.replace(
    '<div class="score-item"><div class="score-label">ELO Model</div><div class="score-value" id="pts-elo">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>',
    '<div class="score-item"><div class="score-label">ELO Model</div><div class="score-value" id="pts-elo">0</div></div>\n<div class="score-item"><div class="score-label">Cup26 AI</div><div class="score-value" id="pts-cup26">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>'
)

# Actualizar scoreboard JS
html = html.replace(
    "document.getElementById('pts-elo').textContent=e;\n  document.getElementById('pts-consensus').textContent=f;",
    "document.getElementById('pts-elo').textContent=e;\n  document.getElementById('pts-cup26').textContent=cup;\n  document.getElementById('pts-consensus').textContent=f;"
)

# Actualizar tabla comparativa header
html = html.replace(
    '<th style="text-align:center">ELO Model</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">ELO</th><th style="text-align:center">Con</th>',
    '<th style="text-align:center">ELO Model</th>\n<th style="text-align:center">Cup26 AI</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">ELO</th><th style="text-align:center">Cup26</th><th style="text-align:center">Con</th>'
)

# Actualizar renderComparativa
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e)',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup)'
)
html = html.replace(
    '${con.agree}/8</td>',
    '${con.agree}/9</td>'
)
html = html.replace(
    '<td style="text-align:center"><span class="pred pred-chatgpt" style="background:#ccfbf1;color:#0f766e">${x.e}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>',
    '<td style="text-align:center"><span class="pred pred-chatgpt" style="background:#ccfbf1;color:#0f766e">${x.e}</span></td>\n    <td style="text-align:center"><span class="pred pred-cascade" style="background:#ffedd5;color:#9a3412">${x.cup}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>'
)
html = html.replace(
    '<td style="text-align:center" id="pts-e-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>',
    '<td style="text-align:center" id="pts-e-${x.id}"></td>\n    <td style="text-align:center" id="pts-cup-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>'
)

# Actualizar renderFinal y renderProde
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e);',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e,x.cup);'
)

# Actualizar updateInputStyle
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup).score);'
)

# Actualizar updateProde
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e,m.cup).score);'
)

# Actualizar min-width de tabla
html = html.replace(
    'min-width:1900px',
    'min-width:2100px'
)

# Actualizar texto de pestaña
html = html.replace(
    'Comparativa 8 IA',
    'Comparativa 9 IA'
)

# Actualizar contador de fuentes en dashboard
html = html.replace(
    '<div class="stat-card"><div class="stat-value" id="stat-sources">8</div><div class="stat-label">Fuentes IA</div></div>',
    '<div class="stat-card"><div class="stat-value" id="stat-sources">9</div><div class="stat-label">Fuentes IA</div></div>'
)

# Actualizar pesos en dashboard chart
html = html.replace(
    "labels:['Cascade','ChatGPT','Gemini','Fansided','ESPN','Yahoo','1960Tips','ELO'],",
    "labels:['Cascade','ChatGPT','Gemini','Fansided','ESPN','Yahoo','1960Tips','ELO','Cup26'],"
)
html = html.replace(
    "data:[1.0,1.0,1.0,0.8,1.3,0.8,1.5,1.5]",
    "data:[1.0,1.0,1.0,0.8,1.3,0.8,1.5,1.5,1.4]"
)
html = html.replace(
    "backgroundColor:['#dbeafe','#f3e8ff','#d1fae5','#fef3c7','#fce7f3','#e0e7ff','#f3e8ff','#ccfbf1']",
    "backgroundColor:['#dbeafe','#f3e8ff','#d1fae5','#fef3c7','#fce7f3','#e0e7ff','#f3e8ff','#ccfbf1','#ffedd5']"
)

# Guardar HTML actualizado
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML actualizado con Cup26 AI como fuente #9")
print(f"Total de partidos actualizados: {len(predictions_cup26)}")
