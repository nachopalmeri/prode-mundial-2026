#!/usr/bin/env python3
"""
Script para agregar predicciones del modelo ELO al HTML del Prode Mundial 2026.
"""

import json
import re

# Leer predicciones del modelo ELO
with open('predictions_elo_model.json', 'r') as f:
    predictions_elo = json.load(f)

# Leer el HTML actual
with open('prode-mundial-2026.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Actualizar los datos de los partidos para incluir ELO (campo 'e')
for match_id, score in predictions_elo.items():
    pattern = rf'({{id:{match_id},gr:"[A-Z]",d:"[^"]+",t:"[^"]+",a:"[^"]+",b:"[^"]+",c:"[^"]+",g:"[^"]+",f:"[^"]+",fs:"[^"]+",esp:"[^"]+",yh:"[^"]+",t:"[^"]+")(,ch:)'
    replacement = rf'\1,e:"{score}"\2'
    html = re.sub(pattern, replacement, html)

# Actualizar getConsensus para 8 fuentes
html = html.replace(
    'function getConsensus(c,g,m,fs,esp,yh,t){',
    'function getConsensus(c,g,m,fs,esp,yh,t,e){'
)
html = html.replace(
    'const scores=[c,g,m,fs,esp,yh,t];',
    'const scores=[c,g,m,fs,esp,yh,t,e];'
)
html = html.replace(
    'const avgA=Math.round(parsed.reduce((a,b)=>a+b.ga,0)/7);\n  const avgB=Math.round(parsed.reduce((a,b)=>a+b.gb,0)/7);',
    'const avgA=Math.round(parsed.reduce((a,b)=>a+b.ga,0)/8);\n  const avgB=Math.round(parsed.reduce((a,b)=>a+b.gb,0)/8);'
)

# Actualizar getMatchPoints para incluir 'e'
html = html.replace(
    "source==='t'?m.t:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score;",
    "source==='t'?m.t:source==='e'?m.e:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score;"
)

# Actualizar updateScores para incluir ELO
html = html.replace(
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,f=0,played=0;',
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,e=0,f=0,played=0;'
)
html = html.replace(
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; f+=pf;",
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pe=getMatchPoints(x.id,'e'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; e+=pe; f+=pf;"
)
html = html.replace(
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-f-'+x.id,pf);",
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-e-'+x.id,pe);setPts('pts-f-'+x.id,pf);"
)

# Agregar scoreboard item para ELO
html = html.replace(
    '<div class="score-item"><div class="score-label">1960Tips</div><div class="score-value" id="pts-1960tips">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>',
    '<div class="score-item"><div class="score-label">1960Tips</div><div class="score-value" id="pts-1960tips">0</div></div>\n<div class="score-item"><div class="score-label">ELO Model</div><div class="score-value" id="pts-elo">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>'
)

# Actualizar scoreboard JS
html = html.replace(
    "document.getElementById('pts-1960tips').textContent=t;\n  document.getElementById('pts-consensus').textContent=f;",
    "document.getElementById('pts-1960tips').textContent=t;\n  document.getElementById('pts-elo').textContent=e;\n  document.getElementById('pts-consensus').textContent=f;"
)

# Actualizar tabla comparativa header
html = html.replace(
    '<th style="text-align:center">1960Tips</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">Con</th>',
    '<th style="text-align:center">1960Tips</th>\n<th style="text-align:center">ELO Model</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">ELO</th><th style="text-align:center">Con</th>'
)

# Actualizar renderComparativa
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t)',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e)'
)
html = html.replace(
    '${con.agree}/7</td>',
    '${con.agree}/8</td>'
)
html = html.replace(
    '<td style="text-align:center"><span class="pred pred-cascade" style="background:#f3e8ff;color:#7c3aed">${x.t}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>',
    '<td style="text-align:center"><span class="pred pred-cascade" style="background:#f3e8ff;color:#7c3aed">${x.t}</span></td>\n    <td style="text-align:center"><span class="pred pred-chatgpt" style="background:#ccfbf1;color:#0f766e">${x.e}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>'
)
html = html.replace(
    '<td style="text-align:center" id="pts-t-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>',
    '<td style="text-align:center" id="pts-t-${x.id}"></td>\n    <td style="text-align:center" id="pts-e-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>'
)

# Actualizar renderFinal y renderProde
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t);',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t,x.e);'
)

# Actualizar updateInputStyle
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score);'
)

# Actualizar updateProde
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t,m.e).score);'
)

# Actualizar min-width de tabla
html = html.replace(
    'min-width:1700px',
    'min-width:1900px'
)

# Actualizar texto de pestaña
html = html.replace(
    'Comparativa 7 IA',
    'Comparativa 8 IA'
)

# Guardar HTML actualizado
with open('prode-mundial-2026.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML actualizado con ELO Model como fuente #8")
print(f"Total de partidos actualizados: {len(predictions_elo)}")
