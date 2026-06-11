#!/usr/bin/env python3
"""Inject dynamic top-3 predictions and dashboard UI into the static HTML."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
PREDICTIONS_PATH = PROJECT_ROOT / "data" / "model" / "latest_predictions.json"


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    if start in text and end in text:
        before = text[: text.index(start)]
        after = text[text.index(end) + len(end) :]
        return before + start + "\n" + replacement.strip() + "\n" + end + after
    return text


def dynamic_json_block(predictions: dict) -> str:
    payload = json.dumps(predictions, ensure_ascii=False, separators=(",", ":"))
    return f"const DYNAMIC_PREDICTIONS={payload};"


DYNAMIC_CSS = r"""
/* Dynamic Top 3 */
.dynamic-hero{position:relative;overflow:hidden;border:1px solid var(--border);border-radius:22px;padding:clamp(18px,3vw,34px);margin-bottom:18px;background:linear-gradient(135deg,color-mix(in oklch,var(--accent) 14%,var(--card)),var(--card));box-shadow:0 16px 50px oklch(0 0 0/.10)}
.dynamic-hero::after{content:'';position:absolute;inset:auto -10% -45% 35%;height:220px;background:radial-gradient(circle,color-mix(in oklch,var(--gold) 28%,transparent),transparent 62%);pointer-events:none}
.dynamic-kicker{font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;color:var(--accent);font-weight:800;margin-bottom:8px}
.dynamic-title{font-family:var(--ff-display);font-size:clamp(2.3rem,7vw,5.4rem);letter-spacing:.03em;line-height:.9;margin-bottom:10px}
.dynamic-sub{max-width:780px;color:var(--text2);font-size:.95rem}
.dynamic-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.meta-pill{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--border);background:color-mix(in oklch,var(--card) 80%,transparent);border-radius:999px;padding:7px 10px;font-size:.72rem;font-weight:700;color:var(--text2)}
.dynamic-toolbar{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin:14px 0}
.dynamic-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}
.pick-card{position:relative;background:var(--card);border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:0 8px 28px oklch(0 0 0/.08);transition:transform .22s var(--ease-out),box-shadow .22s var(--ease-out)}
.pick-card:hover{transform:translateY(-3px);box-shadow:0 18px 42px oklch(0 0 0/.13)}
.pick-top{padding:14px 14px 12px;background:linear-gradient(135deg,color-mix(in oklch,var(--accent) 10%,transparent),transparent)}
.pick-line{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.pick-id{font-size:.68rem;font-weight:800;color:var(--text3);letter-spacing:.08em;text-transform:uppercase}
.pick-status{font-size:.63rem;font-weight:800;border-radius:999px;padding:3px 8px;text-transform:uppercase}
.pick-status.open{background:var(--green-bg);color:var(--green)}
.pick-status.frozen{background:var(--yellow-bg);color:var(--yellow)}
.pick-teams{font-weight:900;font-size:1rem;line-height:1.2;margin-top:8px}
.pick-time{font-size:.72rem;color:var(--text2);margin-top:4px}
.best-pick{display:flex;align-items:baseline;gap:10px;margin-top:12px}
.best-score{font-family:var(--ff-display);font-size:3rem;line-height:.85;color:var(--gold);letter-spacing:.03em}
.best-label{font-size:.68rem;color:var(--text3);text-transform:uppercase;font-weight:800;letter-spacing:.08em}
.top3{padding:12px 14px 14px;display:grid;gap:9px}
.score-row{display:grid;grid-template-columns:48px 1fr 46px;align-items:center;gap:8px}
.score-chip{font-weight:900;text-align:center;border-radius:8px;padding:5px 6px;background:var(--pred-bg);color:var(--pred-text)}
.prob-track{height:10px;border-radius:999px;background:var(--card2);overflow:hidden;border:1px solid var(--border)}
.prob-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--gold))}
.prob-value{text-align:right;font-size:.74rem;font-weight:800;color:var(--text2)}
.pick-footer{border-top:1px solid var(--border);padding:10px 14px;display:flex;justify-content:space-between;gap:10px;font-size:.72rem;color:var(--text2)}
.context-line{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap}
.context-pill{font-size:.62rem;font-weight:800;border-radius:999px;padding:4px 7px;background:color-mix(in oklch,var(--accent) 10%,transparent);color:var(--accent);text-transform:uppercase;letter-spacing:.04em}
.context-pill.played{background:var(--green-bg);color:var(--green)}
.outcome-strip{display:flex;gap:4px;min-width:130px}
.outcome-piece{height:8px;border-radius:999px;background:var(--border)}
.outcome-piece.home{background:var(--green)}
.outcome-piece.draw{background:var(--yellow)}
.outcome-piece.away{background:var(--red)}
.dynamic-empty{padding:28px;text-align:center;color:var(--text2)}
"""


DYNAMIC_SECTION = r"""
<!-- TAB: DINAMICO -->
<div id="tab-dinamico" class="section active">
<div class="dynamic-hero">
<div class="dynamic-kicker">Motor dinámico · Top 3 por partido</div>
<div class="dynamic-title">Picks vivos hasta el cierre</div>
<div class="dynamic-sub">El algoritmo recalcula partidos abiertos con consenso de fuentes, priors de fuerza, matriz de goles y estado del torneo. La Fecha 3 se debe decidir con tabla real, no con predicción fija de hoy.</div>
<div class="dynamic-meta" id="dynamic-meta"></div>
</div>
<div class="dynamic-toolbar">
<div class="date-filters">
<button class="date-filter-btn active" onclick="renderDynamicTop3('all',this)">Todos</button>
<button class="date-filter-btn" onclick="renderDynamicTop3(1,this)">Fecha 1</button>
<button class="date-filter-btn" onclick="renderDynamicTop3(2,this)">Fecha 2</button>
<button class="date-filter-btn" onclick="renderDynamicTop3(3,this)">Fecha 3</button>
</div>
</div>
<div class="dynamic-grid" id="dynamic-grid"></div>
</div>
"""


DYNAMIC_JS = r"""
function dynamicFecha(id){return id<=24?1:id<=48?2:3}
function formatDynamicScore(score){return score.replace('-',' - ')}
function renderDynamicMeta(){
  const meta=document.getElementById('dynamic-meta');
  if(!meta||typeof DYNAMIC_PREDICTIONS==='undefined')return;
  const m=DYNAMIC_PREDICTIONS.metadata;
  meta.innerHTML=`<span class="meta-pill">Modelo ${m.model_version}</span><span class="meta-pill">${m.match_count} partidos</span><span class="meta-pill">${m.source_count} fuentes</span><span class="meta-pill">Actualizado ${new Date(m.generated_at).toLocaleString('es-AR')}</span>`;
}
function renderDynamicTop3(filter='all',btn=null){
  const grid=document.getElementById('dynamic-grid');
  if(!grid||typeof DYNAMIC_PREDICTIONS==='undefined')return;
  if(btn){btn.parentElement.querySelectorAll('.date-filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active')}
  const items=DYNAMIC_PREDICTIONS.matches.filter(x=>filter==='all'||dynamicFecha(x.id)===filter);
  grid.innerHTML=items.map(x=>{
    const top=x.top_scores.map(s=>`<div class="score-row"><div class="score-chip">${formatDynamicScore(s.score)}</div><div class="prob-track"><div class="prob-fill" style="width:${Math.min(100,s.probability*3.2)}%"></div></div><div class="prob-value">${s.probability}%</div></div>`).join('');
    const status=x.freeze?.frozen?'frozen':'open';
    const statusText=x.played?'Jugado':(x.freeze?.frozen?'Congelado':'Abierto');
    const totalOutcome=Math.max(1,x.one_x_two.home+x.one_x_two.draw+x.one_x_two.away);
    const motivation=`<div class="context-line"><span class="context-pill">R${x.motivation?.round||dynamicFecha(x.id)}</span><span class="context-pill">${x.home}: ${x.motivation?.home||'base'}</span><span class="context-pill">${x.away}: ${x.motivation?.away||'base'}</span>${x.played?`<span class="context-pill played">Real ${formatDynamicScore(x.played_result)}</span>`:''}</div>`;
    return `<article class="pick-card">
      <div class="pick-top">
        <div class="pick-line"><div class="pick-id">Partido ${x.id} · Grupo ${x.group}</div><div class="pick-status ${status}">${statusText}</div></div>
        <div class="pick-teams">${x.home} <span style="color:var(--text3);font-weight:600">vs</span> ${x.away}</div>
        <div class="pick-time">${x.date} · ${x.time} AR · Confianza ${x.confidence}</div>
        <div class="best-pick"><div class="best-score">${formatDynamicScore(x.best_pick)}</div><div class="best-label">pick principal</div></div>
        ${motivation}
      </div>
      <div class="top3">${top}</div>
      <div class="pick-footer">
        <span>xG ${x.expected_goals.home} - ${x.expected_goals.away}</span>
        <span>Acuerdo ${x.source_agreement}%</span>
        <div class="outcome-strip" title="Local / Empate / Visitante">
          <div class="outcome-piece home" style="width:${(x.one_x_two.home/totalOutcome)*100}%"></div>
          <div class="outcome-piece draw" style="width:${(x.one_x_two.draw/totalOutcome)*100}%"></div>
          <div class="outcome-piece away" style="width:${(x.one_x_two.away/totalOutcome)*100}%"></div>
        </div>
      </div>
    </article>`;
  }).join('')||'<div class="dynamic-empty">No hay partidos para este filtro.</div>';
}
"""


def ensure_dynamic_dashboard(html: str, predictions: dict) -> str:
    css_block = "/* BEGIN_DYNAMIC_TOP3_CSS */\n" + DYNAMIC_CSS.strip() + "\n/* END_DYNAMIC_TOP3_CSS */"
    if "/* BEGIN_DYNAMIC_TOP3_CSS */" in html:
        html = replace_between(html, "/* BEGIN_DYNAMIC_TOP3_CSS */", "/* END_DYNAMIC_TOP3_CSS */", DYNAMIC_CSS)
    else:
        html = html.replace("/* Reduced motion */", css_block + "\n\n/* Reduced motion */")

    if "onclick=\"showTab('dinamico')\"" not in html:
        html = html.replace(
            '<button class="tab-btn active" onclick="showTab(\'comparativa\')">Comparativa 10 IA</button>',
            '<button class="tab-btn active" onclick="showTab(\'dinamico\')">Top 3 Dinámico</button>\n<button class="tab-btn" onclick="showTab(\'comparativa\')">Comparativa 10 IA</button>',
        )
        html = html.replace('<div id="tab-comparativa" class="section active">', '<div id="tab-comparativa" class="section">')

    if "<!-- TAB: DINAMICO -->" not in html:
        html = html.replace("<!-- TAB: COMPARATIVA -->", DYNAMIC_SECTION.strip() + "\n\n<!-- TAB: COMPARATIVA -->")

    html = html.replace(
        "const map={comparativa:'comparativa',dashboard:'dashboard',final:'final',prode:'prode',noticias:'noticias'};",
        "const map={dinamico:'top 3',comparativa:'comparativa',dashboard:'dashboard',final:'final',prode:'prode',noticias:'noticias'};",
    )

    block = dynamic_json_block(predictions)
    if "/* BEGIN_DYNAMIC_PREDICTIONS */" in html:
        html = replace_between(html, "/* BEGIN_DYNAMIC_PREDICTIONS */", "/* END_DYNAMIC_PREDICTIONS */", block)
    else:
        html = html.replace(
            "const matches = [];",
            "const matches = [];\n/* BEGIN_DYNAMIC_PREDICTIONS */\n" + block + "\n/* END_DYNAMIC_PREDICTIONS */",
        )

    if "function renderDynamicTop3" in html:
        html = replace_between(html, "/* BEGIN_DYNAMIC_TOP3_JS */", "/* END_DYNAMIC_TOP3_JS */", DYNAMIC_JS)
    else:
        html = html.replace("function renderFinal(){", "/* BEGIN_DYNAMIC_TOP3_JS */\n" + DYNAMIC_JS.strip() + "\n/* END_DYNAMIC_TOP3_JS */\n\nfunction renderFinal(){")

    if "renderDynamicMeta();" not in html:
        html = html.replace("  renderComparativa();", "  renderDynamicMeta();\n  renderDynamicTop3();\n  renderComparativa();")

    return html


def main() -> None:
    predictions = json.loads(PREDICTIONS_PATH.read_text(encoding="utf-8"))
    html = HTML_PATH.read_text(encoding="utf-8")
    HTML_PATH.write_text(ensure_dynamic_dashboard(html, predictions), encoding="utf-8")
    print(f"Injected dynamic dashboard using {len(predictions['matches'])} matches")


if __name__ == "__main__":
    main()
