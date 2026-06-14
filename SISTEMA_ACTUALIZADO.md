# Sistema de Predicciones Prode - ACTUALIZACIÓN COMPLETADA

**Fecha:** 13 Jun 2026 20:00 UTC-3  
**Estado:** ✅ Sistema completo con motor bayesiano, ELOs reales de eloratings.net, Smart Picks, 4 partidos jugados

---

## 📊 Resultados de Fecha 1

| Partido | Local | Visitante | Resultado | Sistema | Gana |
|---------|-------|-----------|-----------|---------|------|
| 1 | Mexico | South Africa | 2-0 | 2-0 ✓ | ✓ |
| 2 | South Korea | Czechia | 2-1 | 1-0 ✗ | ✓ |
| 3 | Canada | Bosnia | 1-1 | 2-0 ✗ | ✗ |
| 4 | USA | Paraguay | 4-1 | 1-0 ✗ | ✓ |

**Consenso (weighted): winner_accuracy 75%, exact_accuracy 25%**

---

## 🎯 Cambios Implementados (13 Jun)

### 1️⃣ Pesos Recalibrados por Performance Real (4 partidos)

```
              winner_rate  peso_anterior  peso_nuevo
Cascade:      50%          1.86           1.0
ChatGPT:      50%          1.86           1.0
Gemini:       50%          1.86           1.0
Fansided:     25%          1.45           0.5  ← peor
ESPN:         50%          1.05           1.0
Yahoo:        50%          0.64           0.8
1960Tips:     75%          0.77           2.0  ← mejor
ELO:          50%          1.45           1.2
Cup26:        50%          2.0            1.0
Polymarket:   50%          0.5            1.0
```

**TOTAL_WEIGHT:** 11.9 → 10.5

### 2️⃣ Nuevas Lesiones Confirmadas

| Equipo | Baja | Estado | Fuente |
|--------|------|--------|--------|
| Brazil | Neymar | OUT Mundial | ESPN |
| Brazil | Rodrygo | OUT (ACL) | ESPN |
| Brazil | Estêvão | OUT Mundial | ESPN |
| Morocco | Aguerd | OUT fase grupos | ESPN |
| Morocco | Ez Abde | OUT fase grupos | ESPN |
| Morocco | Mazraoui | DUDA | ESPN |
| Canada | A. Davies | OUT fecha 1 | FIFA |
| Netherlands | Xavi Simons | OUT (ACL) | RotoWire |
| Netherlands | J. Timber | OUT fase grupos | RotoWire |
| Netherlands | De Jong | DUDA | beIN |
| Spain | Pedri | OUT fase grupos | FIFA |
| France | Maignan | DUDA muslo | ESPN |
| USA | Pulisic | LEVE (jugó) | FIFA |

**Impacto:** Brazil -15%, Netherlands -15%, Morocco -15%, Spain -12%

### 3️⃣ Standings Actualizados

**Grupo A:** Mexico 3pts (1p), South Korea 3pts (1p), Czechia 0pts (1p), South Africa 0pts (1p)
**Grupo B:** Canada 1pt (1p), Bosnia 1pt (1p), Qatar 0pts (0p), Switzerland 0pts (0p)
**Grupo D:** USA 3pts (1p), Paraguay 0pts (1p), Australia 0pts (0p), Turkiye 0pts (0p)

### 4️⃣ Archivos Actualizados

- `data/runtime/results.json` — 4 resultados guardados
- `data/runtime/context_adjustments.json` — 7 equipos con penalización
- `data/raw/injuries_20260613_1700.json` — 13 lesiones registradas
- `prode-mundial-2026.html` — Fecha, scores, pesos, accuracy, standings, lesiones

---

## 📈 Accuracy por Fuente (4 partidos)

| Fuente | Winner Rate | Exact Rate | Peso |
|--------|------------|------------|------|
| 1960Tips | 75% (3/4) | 25% (1/4) | 2.0 |
| ELO | 50% (2/4) | 25% (1/4) | 1.2 |
| Cascade | 50% (2/4) | 25% (1/4) | 1.0 |
| ChatGPT | 50% (2/4) | 25% (1/4) | 1.0 |
| Gemini | 50% (2/4) | 25% (1/4) | 1.0 |
| ESPN | 50% (2/4) | 25% (1/4) | 1.0 |
| Yahoo | 50% (2/4) | 25% (1/4) | 0.8 |
| Cup26 | 50% (2/4) | 25% (1/4) | 1.0 |
| Polymarket | 50% (2/4) | 25% (1/4) | 1.0 |
| Fansided | 25% (1/4) | 25% (1/4) | 0.5 |

**Consenso ponderado: 75% winner / 25% exact**

---

## 📋 Pendientes

- [ ] Partidos de hoy: Qatar vs Suiza (19:00), Brazil vs Morocco (22:00), Haiti vs Scotland, Australia vs Turkiye
- [ ] Monitorear lesiones post-partido Brazil vs Morocco (Neymar baja impacta)
- [ ] Verificar actualización de odds Polymarket para mercados en vivo

---

---

## 🧠 Actualización Motor Bayesiano + ELOs Reales (13 Jun 20:00)

### 1️⃣ Nuevo Algoritmo: Bayesian Smart Consensus Engine

| Componente | Descripción |
|-----------|-------------|
| `getSmartConsensus(matchId)` | Reemplaza `getConsensus()` — fusión bayesiana de fuentes + contexto |
| `eloExpectedGoals(team1, team2)` | Expected goals vía diferencia ELO, con injury multiplier |
| `scoreDistribution(xG1, xG2)` | Matriz Poisson 7×7 (0-6 goles) |
| `bayesianFusion(sourceEvidence, prior)` | Blend dinámico: +fuentes si concuerdan, +prior si disienten |
| `outcomeProbs(probs)` | Probabilidades 1X2 |
| `topScores(probs, n)` | Top N resultados por probabilidad |
| Validación Monte Carlo | 1000 simulaciones para calibrar confianza |

**Blend dinámico:** agreement ≥70% → 75% fuentes / 25% prior; agreement ≤40% → 35% fuentes / 65% prior

### 2️⃣ ELO Ratings Reales de eloratings.net (June 13 2026)

Los 48 equipos ahora usan ELO oficial de **eloratings.net** en vez de estimaciones locales. Diferencias principales:

| Equipo | ELO Anterior | ELO Real | Diferencia |
|--------|-------------|----------|------------|
| Spain | 1877 | **2157** | +280 |
| Argentina | 1873 | **2115** | +242 |
| France | 1870 | **2063** | +193 |
| Brazil | 1760 | **1991** | +231 |
| England | 1834 | **2024** | +190 |
| Colombia | 1701 | **1982** | +281 |
| Netherlands | 1756 | **1948** | +192 |
| Germany | 1724 | **1932** | +208 |
| Norway | 1533 | **1914** | +381 |
| Haiti | 1033 | **1548** | +515 |
| Cape Verde | 1170 | **1578** | +408 |

**Fuente:** https://eloratings.net/2026_World_Cup

### 3️⃣ Archivos Actualizados

- `prode-mundial-2026.html` — TEAM_STRENGTHS con ELOs reales, smart picks card
- `data/config/team_strengths.json` — fuente JSON con ELOs reales
- `SISTEMA_ACTUALIZADO.md` — esta bitácora

### 4️⃣ Dashboard Agregado

- **AI Smart Picks card** en tab Dashboard: muestra xG local/visitante, probabilidades 1X2%, top 3 scores, confianza y validación Monte Carlo

---

**Sistema listo para Fecha 2.** Accuracy por fuente será refinada con cada partido jugado.
