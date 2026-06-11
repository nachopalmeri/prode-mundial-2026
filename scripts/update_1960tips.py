#!/usr/bin/env python3
"""
Script para agregar predicciones de 1960tips.com al HTML del Prode Mundial 2026.
"""

import json
import re

# Leer predicciones de 1960tips
with open('../predictions_1960tips.json', 'r') as f:
    predictions_1960tips = json.load(f)

# Leer el HTML actual
with open('../prode-mundial-2026.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Actualizar los datos de los partidos para incluir 1960tips (campo 't')
# Buscar patrones como: {id:1,gr:"A",...,yh:"2-1",ch:"FOX / Tubi"}
# Y agregar t:"X-Y" antes de ch:

for match_id, score in predictions_1960tips.items():
    # Buscar el patrón para este partido
    pattern = rf'({{id:{match_id},gr:"[A-Z]",d:"[^"]+",t:"[^"]+",a:"[^"]+",b:"[^"]+",c:"[^"]+",g:"[^"]+",f:"[^"]+",fs:"[^"]+",esp:"[^"]+",yh:"[^"]+")(,ch:)'
    replacement = rf'\1,t:"{score}"\2'
    html = re.sub(pattern, replacement, html)

# Actualizar getConsensus para 7 fuentes
html = html.replace(
    'function getConsensus(c,g,m,fs,esp,yh){',
    'function getConsensus(c,g,m,fs,esp,yh,t){'
)
html = html.replace(
    'const scores=[c,g,m,fs,esp,yh];',
    'const scores=[c,g,m,fs,esp,yh,t];'
)
html = html.replace(
    'const parsed=scores.map(parseScore);\n  const avgA=Math.round(parsed.reduce((a,b)=>a+b.ga,0)/6);\n  const avgB=Math.round(parsed.reduce((a,b)=>a+b.gb,0)/6);',
    'const parsed=scores.map(parseScore);\n  const avgA=Math.round(parsed.reduce((a,b)=>a+b.ga,0)/7);\n  const avgB=Math.round(parsed.reduce((a,b)=>a+b.gb,0)/7);'
)

# Actualizar getMatchPoints para incluir 't'
html = html.replace(
    "const pred=source==='c'?m.c:source==='g'?m.g:source==='m'?m.f:source==='fs'?m.fs:source==='esp'?m.esp:source==='yh'?m.yh:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh).score;",
    "const pred=source==='c'?m.c:source==='g'?m.g:source==='m'?m.f:source==='fs'?m.fs:source==='esp'?m.esp:source==='yh'?m.yh:source==='t'?m.t:getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score;"
)

# Actualizar updateScores para incluir 1960tips
html = html.replace(
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,f=0,played=0;',
    'let c=0,g=0,m=0,fs=0,esp=0,yh=0,t=0,f=0,played=0;'
)
html = html.replace(
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; f+=pf;",
    "const pc=getMatchPoints(x.id,'c'),pg=getMatchPoints(x.id,'g'),pm=getMatchPoints(x.id,'m'),pfs=getMatchPoints(x.id,'fs'),pesp=getMatchPoints(x.id,'esp'),pyh=getMatchPoints(x.id,'yh'),pt=getMatchPoints(x.id,'t'),pf=getMatchPoints(x.id,'f');\n      c+=pc; g+=pg; m+=pm; fs+=pfs; esp+=pesp; yh+=pyh; t+=pt; f+=pf;"
)
html = html.replace(
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-f-'+x.id,pf);",
    "setPts('pts-c-'+x.id,pc);setPts('pts-g-'+x.id,pg);setPts('pts-m-'+x.id,pm);setPts('pts-fs-'+x.id,pfs);setPts('pts-esp-'+x.id,pesp);setPts('pts-yh-'+x.id,pyh);setPts('pts-t-'+x.id,pt);setPts('pts-f-'+x.id,pf);"
)

# Agregar scoreboard item para 1960tips
html = html.replace(
    '<div class="score-item"><div class="score-label">Yahoo</div><div class="score-value" id="pts-yahoo">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>',
    '<div class="score-item"><div class="score-label">Yahoo</div><div class="score-value" id="pts-yahoo">0</div></div>\n<div class="score-item"><div class="score-label">1960Tips</div><div class="score-value" id="pts-1960tips">0</div></div>\n<div class="score-item"><div class="score-label">Consenso</div>'
)

# Actualizar scoreboard JS
html = html.replace(
    "document.getElementById('pts-yahoo').textContent=yh;\n  document.getElementById('pts-consensus').textContent=f;",
    "document.getElementById('pts-yahoo').textContent=yh;\n  document.getElementById('pts-1960tips').textContent=t;\n  document.getElementById('pts-consensus').textContent=f;"
)

# Actualizar tabla comparativa header
html = html.replace(
    '<th style="text-align:center">Yahoo</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">Con</th>',
    '<th style="text-align:center">Yahoo</th>\n<th style="text-align:center">1960Tips</th>\n<th style="text-align:center">Consenso</th>\n<th style="text-align:center">Acuerdo</th>\n<th style="text-align:center">Real</th>\n<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">1960</th><th style="text-align:center">Con</th>'
)

# Actualizar renderComparativa
html = html.replace(
    'const con=getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh);',
    'const con=getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t);'
)
html = html.replace(
    '${con.agree}/6</td>',
    '${con.agree}/7</td>'
)
html = html.replace(
    '<td style="text-align:center"><span class="pred pred-gemini" style="background:#e0e7ff;color:#3730a3">${x.yh}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>',
    '<td style="text-align:center"><span class="pred pred-gemini" style="background:#e0e7ff;color:#3730a3">${x.yh}</span></td>\n    <td style="text-align:center"><span class="pred pred-cascade" style="background:#f3e8ff;color:#7c3aed">${x.t}</span></td>\n    <td style="text-align:center"><span class="pred pred-consensus">${con.score}</span></td>'
)
html = html.replace(
    '<td style="text-align:center" id="pts-yh-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>',
    '<td style="text-align:center" id="pts-yh-${x.id}"></td>\n    <td style="text-align:center" id="pts-t-${x.id}"></td>\n    <td style="text-align:center" id="pts-f-${x.id}"></td>'
)

# Actualizar renderFinal y renderProde
html = html.replace(
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh);',
    'getConsensus(x.c,x.g,x.f,x.fs,x.esp,x.yh,x.t);'
)

# Actualizar updateInputStyle
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score);'
)

# Actualizar updateProde
html = html.replace(
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh).score);',
    'getConsensus(m.c,m.g,m.f,m.fs,m.esp,m.yh,m.t).score);'
)

# Actualizar min-width de tabla
html = html.replace(
    'min-width:1500px',
    'min-width:1700px'
)

# Actualizar texto de pestaña
html = html.replace(
    'Comparativa 6 IA',
    'Comparativa 7 IA'
)

# Guardar HTML actualizado
with open('../prode-mundial-2026.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML actualizado con 1960tips.com como fuente #7")
print(f"Total de partidos actualizados: {len(predictions_1960tips)}")
