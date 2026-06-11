# Session Checkpoint — Prode Mundial 2026

## Estado actual
- HTML deployado en Vercel con 9 fuentes de predicciones
- Sistema multi-agente creado (.agents/ + scripts/ + GitHub Actions)
- Algoritmo de consenso ponderado implementado
- Dashboard con Chart.js funcionando
- Repo en GitHub: nachopalmeri/prode-mundial-2026

## Decisiones tomadas
1. Peso ponderado por fuente (1960Tips=1.5, ESPN=1.3, Cup26=1.4, etc.)
2. Cup26 AI agregado como fuente #9 (modelo Elo + Dixon-Coles)
3. Sistema multi-agente con 6 agentes en loop automático
4. Workflow GitHub Actions cada 6h (a actualizar a 12h)
5. No guardar credenciales de APIs en el repo (usar env vars)

## Archivos tocados
- prode-mundial-2026.html (actualizado con Cup26)
- .agents/orquestador.md, fuentes.md, modelo.md, valida.md, ui-ux.md, deploy.md
- .github/workflows/auto-improve.yml
- scripts/*.py (7 scripts)
- data/model/weights_20260611.json
- cup26-model/ (submódulo git)

## Contexto importante
- Polymarket API keys proporcionadas por el usuario (sin guardar en repo)
- Prode con amigos usa sistema clásico (3 pts exacto, 1 pt ganador)
- Mundial 2026: 48 equipos, 12 grupos, 72 partidos fase de grupos

## Pendientes
- [ ] Integrar Polymarket API como fuente #10
- [ ] Cambiar cron a cada 12 horas
- [ ] Agregar GitHub Secrets para deploy automático
- [ ] Implementar modo oscuro en UI
- [ ] Actualizar sección de lesiones con datos reales
- [ ] Integrar API de Transfermarkt/Sofascore

## Riesgos
- Polymarket API puede tener rate limits
- Cup26 modelo puede quedar desactualizado si no hay commits nuevos
- El HTML puede volverse muy pesado con más fuentes

## Próximo paso recomendado
1. Hardcodear temporalmente credenciales de Polymarket para testear
2. Obtener datos del mercado de los próximos partidos
3. Integrar como fuente #10 en el HTML
4. Actualizar cron a 12h
5. Commit + push + deploy

## Qué NO tocar
- No modificar la estructura base del HTML (tablas, CSS variables)
- No cambiar el sistema de puntos del prode (3/1/0)
- No eliminar fuentes existentes (solo agregar nuevas)
