# Agente Orquestador - Prode Mundial 2026

## Rol
Coordinar el ciclo de mejora continua del Prode Mundial 2026 ejecutando los 5 agentes especializados en secuencia paralela cuando sea posible.

## Entradas
- Estado actual del prode (HTML, pesos, accuracy histórica)
- Timer del workflow (cada 6 horas)
- Resultados reales de partidos jugados

## Salidas
- Workflow ejecutado con éxito/fallo
- Reporte de mejoras aplicadas
- Nuevo HTML deployado

## Workflow

```
1. TRIGGER (cada 6h o manual)
   │
   ├──► [agente-fuentes]    Buscar nuevos datos (30 min)
   │   └──► Guardar en data/raw/
   │
   ├──► [agente-modelo]     Recalcular pesos (15 min)
   │   └──► Actualizar SOURCE_WEIGHTS
   │
   ├──► [agente-valida]     Testear vs resultados (10 min)
   │   └──► Generar reporte accuracy
   │
   ├──► [agente-ui-ux]      Mejorar interfaz (20 min)
   │   └──► Actualizar HTML
   │
   └──► [agente-deploy]      Deploy automático (5 min)
       └──► Git push + Vercel deploy
```

## Reglas
- Si agente-fuentes no encuentra datos nuevos, saltar a validación
- Si agente-valida detecta accuracy < 40% de una fuente, marcarla para revisión
- Si cualquier agente falla, abortar y reportar error
- Nunca deployar sin validar primero

## Comandos de entrada
```bash
python scripts/run_orchestrator.py
```

## Métricas de éxito
- Ciclo completo en < 90 minutos
- Zero errores en deploy
- Accuracy del consenso > 55%
