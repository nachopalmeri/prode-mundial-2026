#!/usr/bin/env python3
"""
Overhaul prode-mundial-2026.html:
1. Unified single-table comparativa (no more split tables)
2. Prediction highlighting (green/amber/red) for played matches  
3. New "Resultados" tab with played matches + per-source breakdown
4. Improved Accuracy tab with per-match breakdown
"""
import os, re, json

path = os.path.join(os.path.dirname(__file__), '..', 'prode-mundial-2026.html')
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

changes = 0

# ============================================================
# 1. Add CSS for prediction states and resultados
# ============================================================
css_additions = """
/* Prediction state colors */
.pred-exact{background:color-mix(in oklch,oklch(.55 .22 145) 20%,transparent)!important;color:oklch(.55 .22 145)!important;position:relative}
.pred-exact::after{content:"\\u2713";margin-left:3px;font-size:.65rem;opacity:.8}
.pred-winner{background:color-mix(in oklch,oklch(.6 .2 80) 20%,transparent)!important;color:oklch(.6 .2 80)!important;position:relative}
.pred-winner::after{content:"\\uFF5E";margin-left:3px;font-size:.65rem;opacity:.8}
.pred-wrong{background:color-mix(in oklch,oklch(.55 .22 30) 20%,transparent)!important;color:oklch(.55 .22 30)!important;opacity:.7}
/* Real score badge */
.real-score{display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:#fff;font-weight:800;padding:4px 10px;border-radius:8px;font-size:.85rem;min-width:60px;letter-spacing:.03em}
.real-score.played{background:oklch(.55 .22 145)}
/* Resultados tab */
.resultado-card{background:var(--card);border:1px solid var(--border);border-radius:12px;margin-bottom:14px;overflow:hidden}
.resultado-hero{padding:16px;text-align:center;border-bottom:1px solid var(--border)}
.resultado-score{font-size:2rem;font-weight:900;letter-spacing:.06em;margin:8px 0;color:var(--text)}
.resultado-teams{font-size:1.1rem;font-weight:700;margin:4px 0;display:flex;justify-content:center;gap:16px;align-items:center}
.resultado-teams .vs{color:var(--text3);font-weight:400;font-size:.8rem}
.resultado-info{font-size:.72rem;color:var(--text3);margin-top:4px}
.resultado-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:4px;padding:10px 16px}
.resultado-source{display:flex;justify-content:space-between;align-items:center;padding:5px 10px;border-radius:6px;font-size:.78rem;background:var(--card2)}
.resultado-source .rs-name{font-weight:600;color:var(--text2);font-size:.72rem}
.resultado-source .rs-score{font-weight:700}
.resultado-source.exact{background:color-mix(in oklch,oklch(.55 .22 145) 12%,transparent)}
.resultado-source.winner{background:color-mix(in oklch,oklch(.6 .2 80) 12%,transparent)}
.resultado-source.wrong{background:color-mix(in oklch,oklch(.55 .22 30) 8%,transparent);opacity:.7}
.resultado-rank{display:flex;flex-wrap:wrap;gap:6px;padding:8px 16px 16px;justify-content:center}
.resultado-rank-item{display:flex;align-items:center;gap:6px;padding:4px 10px;border-radius:6px;font-size:.75rem;background:var(--card2)}
.resultado-rank-item .rank-pts{font-weight:800;font-size:.9rem}
.resultado-rank-item .rank-label{color:var(--text2)}
"""

# Insert after the last pred class (pred-consensus)
insert_after = ".pred-consensus{background:linear-gradient(135deg,var(--gold),oklch(.6 .2 80));color:#fff;box-shadow:0 2px 6px oklch(from var(--gold) l c h/.35);font-weight:800}"
if insert_after in html:
    html = html.replace(insert_after, insert_after + css_additions)
    changes += 1
    print("Added prediction state CSS")
else:
    print("ERROR: pred-consensus CSS not found")

# ============================================================
# 2. Replace two-card comparativa with unified single table
# ============================================================
old_comparativa_html = """<!-- Desktop table -->
<div class="card desktop-only">
<div class="card-header"><div><div class="card-title">Todas las Predicciones</div><div class="card-sub">12 fuentes &middot; Pas&aacute; el mouse para ver detalle &middot; Ingres&aacute; el resultado real para calcular puntos</div></div></div>
<div class="table-wrap">
<table>
<thead>
<tr>
<th class="sticky-col">#</th><th class="sticky-col-2">Grupo</th><th>Fecha</th><th>Hora</th><th style="min-width:200px">Partido</th>
<th style="text-align:center">Cascade</th><th style="text-align:center">ChatGPT</th><th style="text-align:center">Gemini</th><th style="text-align:center">Fansided</th><th style="text-align:center">ESPN</th><th style="text-align:center">Yahoo</th></tr></thead><tbody id="tbody-comparativa-header"></tbody></table></div></div>

<div class="card desktop-only">
<div class="table-wrap"><table><thead><tr>
<th style="text-align:center">1960Tips</th><th style="text-align:center">ELO</th><th style="text-align:center">Cup26</th><th style="text-align:center">Polym.</th>
<th style="text-align:center">Olor&aacute;culo</th><th style="text-align:center">Engine</th>
<th style="text-align:center">Consenso</th><th style="text-align:center">Conf.</th><th style="text-align:center">Acuerdo</th><th style="text-align:center">Real</th>
<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th><th style="text-align:center">60</th><th style="text-align:center">ELO</th><th style="text-align:center">C26</th><th style="text-align:center">Pol</th><th style="text-align:center">Olo</th><th style="text-align:center">Eng</th><th style="text-align:center">Con</th>
</tr></thead>
<tbody id="tbody-comparativa"></tbody>
</table>
</div>
</div>"""

new_comparativa_html = """<!-- Desktop table - unified -->
<div class="card desktop-only">
<div class="card-header"><div><div class="card-title">Todas las Predicciones</div><div class="card-sub">12 fuentes &middot; Partidos jugados: predicci&oacute;n coloreada seg&uacute;n acierto</div></div></div>
<div class="table-wrap">
<table id="table-comparativa" style="min-width:2000px">
<thead>
<tr>
<th class="sticky-col">#</th><th class="sticky-col-2">Grupo</th><th>Fecha</th><th>Hora</th><th style="min-width:170px">Partido</th>
<th style="text-align:center">Cas</th><th style="text-align:center">GPT</th><th style="text-align:center">Gem</th><th style="text-align:center">Fan</th><th style="text-align:center">Esp</th><th style="text-align:center">Yah</th>
<th style="text-align:center">60</th><th style="text-align:center">ELO</th><th style="text-align:center">C26</th><th style="text-align:center">Pol</th><th style="text-align:center">Olo</th><th style="text-align:center">Eng</th>
<th style="text-align:center">Cons.</th><th style="text-align:center">Conf.</th><th style="text-align:center">Acu.</th><th style="text-align:center">Real</th>
</tr>
</thead>
<tbody id="tbody-comparativa"></tbody>
</table>
</div>
</div>"""

if old_comparativa_html in html:
    html = html.replace(old_comparativa_html, new_comparativa_html)
    changes += 1
    print("Replaced comparativa HTML with unified table")
else:
    print("ERROR: old comparativa HTML not found")
    # Try to find approximate location
    idx = html.find('class="card-header"><div><div class="card-title">Todas las Predicciones</div>')
    if idx > 0:
        print(f"  Found 'Todas las Predicciones' at index {idx}")
    else:
        print("  Could not find 'Todas las Predicciones' either")

# ============================================================
# 3. Add Resultados tab HTML (button + section)
# ============================================================
# 3a. Add tab button after "Accuracy IA"
old_tab_btn = """<button class="tab-btn" onclick="showTab('accuracy');renderAccuracy()">Accuracy IA</button>"""
new_tab_btn = """<button class="tab-btn" onclick="showTab('accuracy');renderAccuracy()">Accuracy IA</button>
<button class="tab-btn" onclick="showTab('resultados')">Resultados</button>"""
if old_tab_btn in html:
    html = html.replace(old_tab_btn, new_tab_btn)
    changes += 1
    print("Added Resultados tab button")
else:
    print("ERROR: Accuracy tab button not found")

# 3b. Add Resultados section after Accuracy section
# Find the end of accuracy section (closing </div> before next tab)
old_accuracy_end = """<div style="padding:10px 0;font-size:.78rem;color:var(--text3);text-align:center">
Los datos se actualizan cada 6h via CI/CD &middot; Ingres&aacute; resultados con <code>python scripts/fetch_results.py</code>
</div>
</div>

</div><!-- /container -->"""

new_accuracy_end = """<div style="padding:10px 0;font-size:.78rem;color:var(--text3);text-align:center">
Los datos se actualizan cada 6h via CI/CD
</div>
</div>

<!-- TAB: RESULTADOS -->
<div id="tab-resultados" class="section">
<div class="resultados-hero" style="text-align:center;padding:14px 0 6px">
<div style="font-size:.8rem;color:var(--text3);margin-bottom:8px;font-weight:600">Partidos jugados &mdash; acierto exacto <span class="pts pts-exact" style="font-size:.7rem;padding:2px 6px">3 pts</span> · solo ganador <span class="pts pts-winner" style="font-size:.7rem;padding:2px 6px">1 pt</span></div>
</div>
<div id="resultados-container"></div>
</div>

</div><!-- /container -->"""

if old_accuracy_end in html:
    html = html.replace(old_accuracy_end, new_accuracy_end)
    changes += 1
    print("Added Resultados section HTML")
else:
    print("ERROR: accuracy end not found")
    # Try without the </div><!-- /container -->
    alt_end = """<div style="padding:10px 0;font-size:.78rem;color:var(--text3);text-align:center">
Los datos se actualizan cada 6h via CI/CD &middot; Ingres&aacute; resultados con <code>python scripts/fetch_results.py</code>
</div>
</div>

</div><!-- /container -->"""
    if alt_end in html:
        html = html.replace(alt_end, new_accuracy_end)
        changes += 1
        print("Added Resultados section HTML (alt)")
    else:
        print("ERROR: accuracy alt end not found")

# ============================================================
# 4. Rewrite renderComparativa() JS
# ============================================================
old_render = """function renderComparativa(){
  const tb=document.getElementById('tbody-comparativa');
  const tbh=document.getElementById('tbody-comparativa-header');
  // Header part (group, date, match)
  matches.forEach(x=>{
    const con=getSmartConsensus(x.id);
    const fechaNum=getFecha(x.id);
    const trh=document.createElement('tr');trh.id='row-'+x.id;trh.className=getFechaClass(x.id);
    trh.innerHTML=`<td class="sticky-col">${x.id}</td><td class="sticky-col-2"><span class="group-badge">${x.gr}</span></td><td class="date-cell">${x.d}<span class="date-badge date-badge-${fechaNum}">F${fechaNum}</span></td><td class="date-cell">${x.h}</td><td style="min-width:200px" class="match-cell">${x.a} <span class="vs" style="color:var(--text3);font-weight:400">vs</span> ${x.b}</td>
    <td style="text-align:center"><span class="pred pred-cascade">${x.c}</span></td>
    <td style="text-align:center"><span class="pred pred-chatgpt">${x.g}</span></td>
    <td style="text-align:center"><span class="pred pred-gemini">${x.f}</span></td>
    <td style="text-align:center"><span class="pred pred-fansided">${x.fs}</span></td>
    <td style="text-align:center"><span class="pred pred-espn">${x.esp}</span></td>
    <td style="text-align:center"><span class="pred pred-yahoo">${x.yh}</span></td>`;
    tbh.appendChild(trh);

    const tr=document.createElement('tr');tr.className=getFechaClass(x.id);
    tr.innerHTML=
    `<td style="text-align:center"><span class="pred pred-1960tips">${x.tips}</span></td>
    <td style="text-align:center"><span class="pred pred-elo">${x.e}</span></td>
    <td style="text-align:center"><span class="pred pred-cup26">${x.cup}</span></td>
    <td style="text-align:center"><span class="pred pred-polymarket">${x.pm}</span></td>
    <td style="text-align:center"><span class="pred pred-oloraculo">${OLORACULO_PREDS[x.id]||'-'}</span></td>
    <td style="text-align:center"><span class="pred pred-engine">${ENGINE_PREDS[x.id]||'-'}</span></td>
    <td style="text-align:center"><span class="pred pred-consensus" style="font-size:.85rem">${con.score}</span></td>
    <td style="text-align:center"><span class="conf-badge conf-${con.confidence}">${con.confidence==='high'?'Alta':con.confidence==='medium'?'Media':'Baja'}</span></td>
    <td style="text-align:center" class="${con.agree>=7?'agree-3':con.agree>=4?'agree-2':'agree-1'}">${con.agree}/10</td>
    <td style="text-align:center"><input type="text" class="input-real" id="real-${x.id}" placeholder="X-Y" maxlength="5" oninput="updateInputStyle(this,${x.id});updateScores()"></td>
    <td style="text-align:center" id="pts-c-${x.id}"></td>
    <td style="text-align:center" id="pts-g-${x.id}"></td>
    <td style="text-align:center" id="pts-m-${x.id}"></td>
    <td style="text-align:center" id="pts-fs-${x.id}"></td>
    <td style="text-align:center" id="pts-esp-${x.id}"></td>
    <td style="text-align:center" id="pts-yh-${x.id}"></td>
    <td style="text-align:center" id="pts-t-${x.id}"></td>
    <td style="text-align:center" id="pts-e-${x.id}"></td>
    <td style="text-align:center" id="pts-cup-${x.id}"></td>
    <td style="text-align:center" id="pts-pm-${x.id}"></td>
    <td style="text-align:center" id="pts-ol-${x.id}"></td>
    <td style="text-align:center" id="pts-en-${x.id}"></td>
    <td style="text-align:center" id="pts-f-${x.id}"></td>`;
    tb.appendChild(tr);
  });

  // Mobile cards
  const mc=document.getElementById('mobile-cards');
  matches.forEach(x=>{
    const con=getSmartConsensus(x.id);
    const fechaNum=getFecha(x.id);
    const sourceKeys=['c','g','f','fs','esp','yh','tips','e','cup','pm','ol','en'];
    const sourceGrid=sourceKeys.map(k=>{
      let val;
      if(k==='ol') val=OLORACULO_PREDS[x.id]||'-';
      else if(k==='en') val=ENGINE_PREDS[x.id]||'-';
      else val=x[k];
      return `<div class="source-item"><span class="source-name">${SOURCE_LABELS[k]}</span><span class="source-score" style="color:var(--accent)">${val}</span></div>`;
    }).join('');

    const card=document.createElement('div');card.className='match-card';card.id='mcard-'+x.id;
    card.innerHTML=
    `<div class="match-card-header" onclick="toggleMatchCard(${x.id})">
      <span class="group-badge">${x.gr}</span>
      <span class="date-badge date-badge-${fechaNum}" style="font-size:.6rem">F${fechaNum}</span>
      <span class="match-teams">${x.a} vs ${x.b}</span>
      <span class="consensus-badge">${con.score}</span>
      <span class="expand-icon">&#x25BC;</span>
    </div>
    <div class="match-card-body">
      <div class="match-detail"><span>${x.d} &middot; ${x.h} &middot; ${x.ch}</span><span style="font-size:.7rem;color:var(--text3)">${con.agree}/10 acuerdan</span></div>
      <div class="source-grid">${sourceGrid}</div>
      <div class="real-input-wrap">
        <label>Resultado real:</label>
        <input type="text" class="input-real" data-match="${x.id}" placeholder="X-Y" maxlength="5" oninput="syncMobileScore(this)">
      </div>
    </div>`;
    mc.appendChild(card);
  });
}"""

new_render = """function renderComparativa(){
  const tb=document.getElementById('tbody-comparativa');
  const realScores=typeof EMBEDDED_REAL_SCORES!=='undefined'?EMBEDDED_REAL_SCORES:{};
  const sourceKeys=['c','g','f','fs','esp','yh','tips','e','cup','pm','ol','en'];
  const sourceLabels={c:'Cas',g:'GPT',f:'Gem',fs:'Fan',esp:'Esp',yh:'Yah',tips:'60',e:'ELO',cup:'C26',pm:'Pol',ol:'Olo',en:'Eng'};
  const sourceClassMap={c:'pred-cascade',g:'pred-chatgpt',f:'pred-gemini',fs:'pred-fansided',esp:'pred-espn',yh:'pred-yahoo',tips:'pred-1960tips',e:'pred-elo',cup:'pred-cup26',pm:'pred-polymarket',ol:'pred-oloraculo',en:'pred-engine'};
  const getSourceScore=(x,k)=>{
    if(k==='ol') return OLORACULO_PREDS[x.id]||'-';
    if(k==='en') return ENGINE_PREDS[x.id]||'-';
    return x[k]||'-';
  };
  matches.forEach(x=>{
    const con=getSmartConsensus(x.id);
    const fechaNum=getFecha(x.id);
    const realStr=realScores[x.id]||null;
    const tr=document.createElement('tr');tr.id='row-'+x.id;tr.className=getFechaClass(x.id);

    // Match info columns
    let html=`<td class="sticky-col">${x.id}</td><td class="sticky-col-2"><span class="group-badge">${x.gr}</span></td><td class="date-cell">${x.d}<span class="date-badge date-badge-${fechaNum}">F${fechaNum}</span></td><td class="date-cell">${x.h}</td><td style="min-width:170px" class="match-cell">${x.a} <span class="vs" style="color:var(--text3);font-weight:400">vs</span> ${x.b}</td>`;

    // 12 source predictions with highlighting
    sourceKeys.forEach(k=>{
      const score=getSourceScore(x,k);
      let stateClass='';
      if(realStr){
        const e=evaluate(realStr,score);
        if(e==='exact') stateClass=' pred-exact';
        else if(e==='winner') stateClass=' pred-winner';
        else stateClass=' pred-wrong';
      }
      html+=`<td style="text-align:center"><span class="pred ${sourceClassMap[k]}${stateClass}">${score}</span></td>`;
    });

    // Consensus, Confidence, Agreement, Real
    const realHtml=realStr?`<span class="real-score played">${realStr}</span>`:`<input type="text" class="input-real" id="real-${x.id}" placeholder="X-Y" maxlength="5" oninput="updateInputStyle(this,${x.id});updateScores()">`;
    html+=`<td style="text-align:center"><span class="pred pred-consensus" style="font-size:.82rem">${con.score}</span></td>
    <td style="text-align:center"><span class="conf-badge conf-${con.confidence}">${con.confidence==='high'?'Alta':con.confidence==='medium'?'Media':'Baja'}</span></td>
    <td style="text-align:center" class="${con.agree>=7?'agree-3':con.agree>=4?'agree-2':'agree-1'}">${con.agree}/10</td>
    <td style="text-align:center">${realHtml}</td>`;
    tr.innerHTML=html;
    tb.appendChild(tr);
  });

  // Mobile cards
  const mc=document.getElementById('mobile-cards');
  matches.forEach(x=>{
    const con=getSmartConsensus(x.id);
    const fechaNum=getFecha(x.id);
    const realStr=realScores[x.id]||null;
    const getScore=(k)=>{
      if(k==='ol') return OLORACULO_PREDS[x.id]||'-';
      if(k==='en') return ENGINE_PREDS[x.id]||'-';
      return x[k]||'-';
    };
    const sourceGrid=sourceKeys.map(k=>{
      const val=getScore(k);
      let stateClass='';
      if(realStr){
        const e=evaluate(realStr,val);
        if(e==='exact') stateClass=' exact';
        else if(e==='winner') stateClass=' winner';
        else stateClass=' wrong';
      }
      return `<div class="source-item${stateClass}"><span class="source-name">${SOURCE_LABELS[k]}</span><span class="source-score">${val}</span></div>`;
    }).join('');

    const realHtml=realStr?`<div class="real-input-wrap"><label>Resultado real:</label><span class="real-score played">${realStr}</span></div>`:`<div class="real-input-wrap"><label>Resultado real:</label><input type="text" class="input-real" data-match="${x.id}" placeholder="X-Y" maxlength="5" oninput="syncMobileScore(this)"></div>`;

    const card=document.createElement('div');card.className='match-card';card.id='mcard-'+x.id;
    card.innerHTML=
    `<div class="match-card-header" onclick="toggleMatchCard(${x.id})">
      <span class="group-badge">${x.gr}</span>
      <span class="date-badge date-badge-${fechaNum}" style="font-size:.6rem">F${fechaNum}</span>
      <span class="match-teams">${x.a} vs ${x.b}</span>
      <span class="consensus-badge">${con.score}</span>
      <span class="expand-icon">&#x25BC;</span>
    </div>
    <div class="match-card-body">
      <div class="match-detail"><span>${x.d} &middot; ${x.h} &middot; ${x.ch}</span><span style="font-size:.7rem;color:var(--text3)">${con.agree}/10 acuerdan</span></div>
      <div class="source-grid">${sourceGrid}</div>
      ${realHtml}
    </div>`;
    mc.appendChild(card);
  });
}"""

if old_render in html:
    html = html.replace(old_render, new_render)
    changes += 1
    print("Replaced renderComparativa()")
else:
    print("ERROR: renderComparativa() not found")
    # Print first 200 chars of what we're looking for
    print(f"  Looking for: {old_render[:100]}...")

# ============================================================
# 5. Add renderResultados() function
# ============================================================
# Insert after renderComparativa() ends (before /* BEGIN_DYNAMIC_TOP3_JS */)
old_dynamic_js = "/* BEGIN_DYNAMIC_TOP3_JS */"
new_resultados_js = """function renderResultados(){
  const container=document.getElementById('resultados-container');
  const realScores=typeof EMBEDDED_REAL_SCORES!=='undefined'?EMBEDDED_REAL_SCORES:{};
  const playedIds=Object.keys(realScores).map(Number).sort((a,b)=>a-b);
  if(playedIds.length===0){
    container.innerHTML='<div class="card" style="text-align:center;padding:30px;color:var(--text3);font-size:.9rem">Aun no hay partidos jugados. Los resultados apareceran automaticamente aqui.</div>';
    return;
  }
  const sourceKeys=['c','g','f','fs','esp','yh','tips','e','cup','pm','ol','en'];
  const getScore=(m,k)=>{
    if(k==='ol') return OLORACULO_PREDS[m.id]||'-';
    if(k==='en') return ENGINE_PREDS[m.id]||'-';
    return m[k]||'-';
  };
  // Per-source running totals
  const totals={};
  sourceKeys.forEach(k=>{totals[k]={exact:0,winner:0,wrong:0,total:0}});
  let consensusExact=0,consensusWinner=0,consensusWrong=0;
  let html='';
  playedIds.forEach(id=>{
    const m=matches.find(x=>x.id===id);
    if(!m)return;
    const con=getSmartConsensus(m.id);
    const realStr=realScores[id];
    const fechaNum=getFecha(m.id);
    // Evaluate consensus
    const ce=evaluate(realStr,con.score);
    if(ce==='exact') consensusExact++;
    else if(ce==='winner') consensusWinner++;
    else consensusWrong++;
    // Per-source
    let sourceRows='';
    sourceKeys.forEach(k=>{
      const score=getScore(m,k);
      const e=evaluate(realStr,score);
      let state='wrong',pts=0;
      if(e==='exact'){state='exact';pts=3;totals[k].exact++}
      else if(e==='winner'){state='winner';pts=1;totals[k].winner++}
      else totals[k].wrong++;
      totals[k].total+=pts;
      sourceRows+=`<div class="resultado-source ${state}"><span class="rs-name">${SOURCE_LABELS[k]}</span><span class="rs-score">${score} <span style="font-size:.65rem;opacity:.6">+${pts}</span></span></div>`;
    });
    html+=`<div class="resultado-card">
      <div class="resultado-hero">
        <div style="font-size:.75rem;color:var(--text2);font-weight:600">${m.gr} &middot; ${m.d} &middot; ${m.h}</div>
        <div class="resultado-teams"><span>${m.a}</span> <span class="vs">vs</span> <span>${m.b}</span></div>
        <div class="resultado-score">${realStr}</div>
        <div style="font-size:.72rem;color:var(--text3)">Consenso: ${con.score} <span class="conf-badge conf-${con.confidence}" style="font-size:.6rem;margin-left:4px">${con.confidence==='high'?'Alta':con.confidence==='medium'?'Media':'Baja'}</span></div>
      </div>
      <div class="resultado-grid">${sourceRows}</div>
    </div>`;
  });
  // Ranking
  const sorted=sourceKeys.map(k=>({key:k,label:SOURCE_LABELS[k],pts:totals[k].total,exact:totals[k].exact,winner:totals[k].winner,wrong:totals[k].wrong})).sort((a,b)=>b.pts-a.pts);
  let rankHtml='<div class="card"><div class="card-header"><div><div class="card-title">Ranking de Fuentes</div><div class="card-sub">Puntos acumulados en partidos jugados</div></div></div><div class="resultado-rank">';
  // Consensus
  const cPts=consensusExact*3+consensusWinner*1;
  rankHtml+=`<div class="resultado-rank-item" style="background:color-mix(in oklch,var(--gold) 12%,transparent)"><span class="rank-pts" style="color:var(--gold)">${cPts}</span><span class="rank-label"><strong>Consenso</strong></span><span style="font-size:.6rem;color:var(--text3)">${consensusExact}E ${consensusWinner}G ${consensusWrong}M</span></div>`;
  sorted.forEach(s=>{
    const bar=`<span style="display:inline-flex;gap:2px;margin-left:4px"><span style="display:inline-block;width:${Math.max(4,s.exact*4)}px;height:4px;background:oklch(.55 .22 145);border-radius:2px"></span><span style="display:inline-block;width:${Math.max(4,s.winner*4)}px;height:4px;background:oklch(.6 .2 80);border-radius:2px"></span><span style="display:inline-block;width:${Math.max(4,s.wrong*4)}px;height:4px;background:oklch(.55 .22 30);border-radius:2px;opacity:.3"></span></span>`;
    rankHtml+=`<div class="resultado-rank-item"><span class="rank-pts">${s.pts}</span><span class="rank-label">${s.label}</span>${bar}</div>`;
  });
  rankHtml+='</div></div>';
  container.innerHTML=html+rankHtml;
}
""" + old_dynamic_js

if old_dynamic_js in html:
    html = html.replace(old_dynamic_js, new_resultados_js)
    changes += 1
    print("Added renderResultados()")
else:
    print("ERROR: dynamic JS marker not found")

# ============================================================
# 6. Improve renderAccuracy() - add per-match breakdown
# ============================================================
old_accuracy_func = """function renderAccuracy(){
  const tbody = document.getElementById('accuracy-tbody');
  const summaryCard = document.getElementById('accuracy-summary-card');
  const consensusCard = document.getElementById('accuracy-consensus-card');
  const summary = document.getElementById('accuracy-summary');
  const consensusEl = document.getElementById('accuracy-consensus');

  if(!ACCURACY_DATA || !ACCURACY_DATA.sources){
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--text3)">Aún no hay datos de accuracy. Ingresá resultados con <code>python scripts/fetch_results.py</code> y corré <code>python scripts/recalibrate.py</code>.</td></tr>';
    return;
  }

  const src = ACCURACY_DATA.sources;
  let html = '';
  for(const key of SOURCE_KEYS){
    const s = src[key];
    if(!s || s.samples === 0){
      html += `<tr><td>${SOURCE_LABELS[key]||key}</td><td colspan="6" style="text-align:center;color:var(--text3)">Sin datos</td></tr>`;
      continue;
    }
    const ci = s.confidence_index || 0;
    let status, statusClass;
    if(ci >= 30){ status = 'Buena'; statusClass = 'conf-high'; }
    else if(ci >= 15){ status = 'Media'; statusClass = 'conf-medium'; }
    else { status = 'Baja'; statusClass = 'conf-badge'; }
    html += `<tr>
      <td><strong>${s.label || SOURCE_LABELS[key]}</strong></td>
      <td style="text-align:center">${s.exact_accuracy.toFixed(1)}%</td>
      <td style="text-align:center">${s.winner_accuracy.toFixed(1)}%</td>
      <td style="text-align:center">${ci.toFixed(1)}</td>
      <td style="text-align:center">${s.samples}</td>
      <td style="text-align:center">${(s.current_weight||1.0).toFixed(2)}</td>
      <td style="text-align:center"><span class="conf-badge ${statusClass}">${status}</span></td>
    </tr>`;
  }
  tbody.innerHTML = html;

  // Global winrate
  if(ACCURACY_DATA.global_winrate){
    summaryCard.style.display = 'block';
    const g = ACCURACY_DATA.global_winrate;
    const exactClass = g.exact_accuracy >= 50 ? 'conf-high' : 'conf-badge';
    const winnerClass = g.winner_accuracy >= 60 ? 'conf-high' : 'conf-badge';
    summary.innerHTML = `
      <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center">
        <div><span class="conf-badge ${winnerClass}" style="font-size:1.4rem;padding:8px 16px">${g.winner_accuracy}%</span><br><span style="font-size:.75rem;color:var(--text3)">Ganador global</span></div>
        <div><span class="conf-badge ${exactClass}" style="font-size:1rem;padding:6px 12px">${g.exact_accuracy}%</span><br><span style="font-size:.75rem;color:var(--text3)">Exacto global</span></div>
        <div style="font-size:.8rem;color:var(--text2)">${ACCURACY_DATA.matches_analyzed} partido(s) analizados · ${new Date(ACCURACY_DATA.timestamp).toLocaleString()}</div>
      </div>`;
  }

  // Consensus comparison (if available from validation report)
  if(ACCURACY_DATA.consensus){
    consensusCard.style.display = 'block';
    consensusEl.innerHTML = `
      <p>Exacto: <strong>${ACCURACY_DATA.consensus.exact_accuracy}%</strong> · Ganador: <strong>${ACCURACY_DATA.consensus.winner_accuracy}%</strong></p>`;
  }
}"""

new_accuracy_func = """function renderAccuracy(){
  const tbody = document.getElementById('accuracy-tbody');
  const summaryCard = document.getElementById('accuracy-summary-card');
  const consensusCard = document.getElementById('accuracy-consensus-card');
  const summary = document.getElementById('accuracy-summary');
  const consensusEl = document.getElementById('accuracy-consensus');

  if(!ACCURACY_DATA || !ACCURACY_DATA.sources){
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--text3)">Aún no hay datos de accuracy.</td></tr>';
    return;
  }

  // Calculate per-source stats from real scores
  const realScores=typeof EMBEDDED_REAL_SCORES!=='undefined'?EMBEDDED_REAL_SCORES:{};
  const playedIds=Object.keys(realScores).map(Number);
  const sourceKeys=['c','g','f','fs','esp','yh','tips','e','cup','pm','ol','en'];
  const getScore=(m,k)=>{
    if(k==='ol') return OLORACULO_PREDS[m.id]||'-';
    if(k==='en') return ENGINE_PREDS[m.id]||'-';
    return m[k]||'-';
  };
  // Compute live accuracy from real scores
  const liveStats={};
  sourceKeys.forEach(k=>{liveStats[k]={exact:0,winner:0,wrong:0,total:0}});
  playedIds.forEach(id=>{
    const m=matches.find(x=>x.id===id);
    if(!m)return;
    const r=realScores[id];
    sourceKeys.forEach(k=>{
      const s=getScore(m,k);
      const e=evaluate(r,s);
      if(e==='exact') liveStats[k].exact++;
      else if(e==='winner') liveStats[k].winner++;
      else liveStats[k].wrong++;
      liveStats[k].total++;
    });
  });

  const src = ACCURACY_DATA.sources;
  let html = '';
  // Sort sources by exact accuracy descending
  const sorted=sourceKeys.slice().sort((a,b)=>{
    const la=liveStats[a],lb=liveStats[b];
    const ea=la.total>0?la.exact/la.total:0;
    const eb=lb.total>0?lb.exact/lb.total:0;
    if(ea!==eb)return eb-ea;
    const wa=la.total>0?(la.exact+la.winner)/la.total:0;
    const wb=lb.total>0?(lb.exact+lb.winner)/lb.total:0;
    return wb-wa;
  });
  for(const key of sorted){
    const s = src[key];
    const ls=liveStats[key];
    const total=ls?ls.total:0;
    const exactPct=total>0?Math.round(ls.exact/total*1000)/10:0;
    const winPct=total>0?Math.round((ls.exact+ls.winner)/total*1000)/10:0;
    if(!s||total===0){
      html += `<tr><td><strong>${SOURCE_LABELS[key]||key}</strong></td><td colspan="6" style="text-align:center;color:var(--text3)">Sin datos</td></tr>`;
      continue;
    }
    const ci = s.confidence_index || 0;
    let status, statusClass;
    if(ci >= 30){ status = 'Buena'; statusClass = 'conf-high'; }
    else if(ci >= 15){ status = 'Media'; statusClass = 'conf-medium'; }
    else { status = 'Baja'; statusClass = 'conf-badge'; }
    // Visual bar
    const exactBar=Math.max(4,exactPct*1.2);
    const winnerOnlyBar=Math.max(2,(winPct-exactPct)*1.2);
    const wrongBar=Math.max(2,(100-winPct)*1.2);
    const barHtml=`<span style="display:inline-flex;gap:2px;align-items:center;height:16px"><span style="display:inline-block;width:${exactBar}px;height:10px;background:oklch(.55 .22 145);border-radius:3px" title="Exacto ${exactPct}%"></span><span style="display:inline-block;width:${winnerOnlyBar}px;height:10px;background:oklch(.6 .2 80);border-radius:3px" title="Ganador ${(winPct-exactPct).toFixed(1)}%"></span><span style="display:inline-block;width:${wrongBar}px;height:10px;background:oklch(.55 .22 30);border-radius:3px;opacity:.2" title="Error ${(100-winPct).toFixed(1)}%"></span></span>`;
    // Per-match breakdown
    let matchDetail='';
    if(playedIds.length>0){
      matchDetail='<div style="font-size:.65rem;margin-top:4px;display:flex;flex-wrap:wrap;gap:3px;max-width:200px">';
      playedIds.forEach(id=>{
        const m=matches.find(x=>x.id===id);
        if(!m)return;
        const score=getScore(m,key);
        const r=realScores[id];
        const e=evaluate(r,score);
        let cls='pts-wrong';
        if(e==='exact') cls='pts-exact';
        else if(e==='winner') cls='pts-winner';
        matchDetail+=`<span title="#${id} ${m.a}vs${m.b}: pred ${score} real ${r}" class="${cls}" style="padding:1px 4px;border-radius:3px;font-size:.6rem;cursor:default">${id}</span>`;
      });
      matchDetail+='</div>';
    }
    html += `<tr>
      <td><strong>${s.label || SOURCE_LABELS[key]}</strong></td>
      <td style="text-align:center;font-weight:700;color:oklch(.55 .22 145)">${exactPct}%</td>
      <td style="text-align:center;font-weight:600;color:oklch(.6 .2 80)">${winPct}%</td>
      <td style="text-align:center">${barHtml}</td>
      <td style="text-align:center">${ci.toFixed(0)}</td>
      <td style="text-align:center">${total}</td>
      <td style="text-align:center">${(s.current_weight||1.0).toFixed(2)}</td>
      <td style="text-align:center"><span class="conf-badge ${statusClass}">${status}</span></td>
      <td>${matchDetail}</td>
    </tr>`;
  }
  tbody.innerHTML = html;

  // Global winrate
  if(ACCURACY_DATA.global_winrate){
    summaryCard.style.display = 'block';
    const g = ACCURACY_DATA.global_winrate;
    const exactClass = g.exact_accuracy >= 50 ? 'conf-high' : 'conf-badge';
    const winnerClass = g.winner_accuracy >= 60 ? 'conf-high' : 'conf-badge';
    summary.innerHTML = `
      <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center">
        <div><span class="conf-badge ${winnerClass}" style="font-size:1.4rem;padding:8px 16px">${g.winner_accuracy}%</span><br><span style="font-size:.75rem;color:var(--text3)">Ganador global</span></div>
        <div><span class="conf-badge ${exactClass}" style="font-size:1rem;padding:6px 12px">${g.exact_accuracy}%</span><br><span style="font-size:.75rem;color:var(--text3)">Exacto global</span></div>
        <div style="font-size:.8rem;color:var(--text2)">${ACCURACY_DATA.matches_analyzed} partido(s) analizados</div>
      </div>`;
  }

  // Consensus from live data
  if(playedIds.length>0){
    let cExact=0,cWinner=0,cWrong=0;
    playedIds.forEach(id=>{
      const m=matches.find(x=>x.id===id);
      if(!m)return;
      const con=getSmartConsensus(id);
      const e=evaluate(realScores[id],con.score);
      if(e==='exact') cExact++;
      else if(e==='winner') cWinner++;
      else cWrong++;
    });
    const cTotal=cExact+cWinner+cWrong;
    const cExactPct=cTotal>0?Math.round(cExact/cTotal*1000)/10:0;
    const cWinPct=cTotal>0?Math.round((cExact+cWinner)/cTotal*1000)/10:0;
    consensusCard.style.display = 'block';
    consensusEl.innerHTML = `
      <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
        <span>Exacto: <strong style="color:oklch(.55 .22 145)">${cExactPct}%</strong> (${cExact}/${cTotal})</span>
        <span>Ganador: <strong style="color:oklch(.6 .2 80)">${cWinPct}%</strong> (${cExact+cWinner}/${cTotal})</span>
        <span>Puntos: <strong>${cExact*3+cWinner*1}</strong></span>
      </div>`;
  }
}"""

# Find old accuracy function and replace it
if old_accuracy_func in html:
    html = html.replace(old_accuracy_func, new_accuracy_func)
    changes += 1
    print("Replaced renderAccuracy()")
else:
    print("ERROR: renderAccuracy() not found")

# ============================================================
# 7. Update accuracy table header for new columns
# ============================================================
old_acc_header = """<th>Fuente</th><th style="text-align:center">Exacta</th><th style="text-align:center">Ganador</th><th style="text-align:center">Confianza</th><th style="text-align:center">Muestras</th><th style="text-align:center">Peso Actual</th><th style="text-align:center">Estado</th>"""
new_acc_header = """<th>Fuente</th><th style="text-align:center">Exacta</th><th style="text-align:center">Acierto</th><th style="text-align:center">Barra</th><th style="text-align:center">Conf.</th><th style="text-align:center">Muestras</th><th style="text-align:center">Peso</th><th style="text-align:center">Estado</th><th style="text-align:center">Partido</th>"""
if old_acc_header in html:
    html = html.replace(old_acc_header, new_acc_header)
    changes += 1
    print("Updated accuracy table header")
else:
    print("ERROR: accuracy header not found")

# ============================================================
# 8. Update init() to call renderResultados on tab switch
# ============================================================
old_showtab = """function showTab(id){
  const map={dinamico:'top 3',comparativa:'comparativa',dashboard:'dashboard',final:'final',prode:'prode',noticias:'noticias'};
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.textContent.toLowerCase().includes(map[id])));
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  const tab=document.getElementById('tab-'+id);
  tab.classList.add('active');
  // Trigger charts if dashboard
  if(id==='dashboard'&&!window._chartsDrawn){drawDashboard();window._chartsDrawn=true}
}"""

new_showtab = """function showTab(id){
  const map={dinamico:'top 3',comparativa:'comparativa',dashboard:'dashboard',final:'final',prode:'prode',noticias:'noticias',accuracy:'accuracy ia',resultados:'resultados'};
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.textContent.toLowerCase().includes(map[id])));
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  const tab=document.getElementById('tab-'+id);
  tab.classList.add('active');
  // Trigger charts if dashboard
  if(id==='dashboard'&&!window._chartsDrawn){drawDashboard();window._chartsDrawn=true}
  // Trigger resultados
  if(id==='resultados'){renderResultados()}
}"""

if old_showtab in html:
    html = html.replace(old_showtab, new_showtab)
    changes += 1
    print("Updated showTab()")
else:
    print("ERROR: showTab() not found")


# ============================================================
# 9. Write out
# ============================================================
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n=== Done: {changes} changes made ===")
