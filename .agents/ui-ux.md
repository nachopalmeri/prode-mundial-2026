# Agente UI-UX - Prode Mundial 2026

## Rol
Mejorar la interfaz del prode según el estado del torneo y feedback de uso.

## Responsabilidades

### 1. Actualizar Dashboard
- Goles por grupo (actualizar después de cada fecha)
- Ranking de fuentes por accuracy
- Gráfico de evolución de confianza

### 2. Optimizar Mobile
- Responsive table con scroll horizontal
- Tabs accesibles con touch
- Inputs grandes para fácil edición

### 3. Nuevas Features UI
- **Modo oscuro**: toggle dark/light
- **Notificaciones**: alertas cuando hay lesiones de último momento
- **Exportar**: CSV/JSON de predicciones
- **Compartir**: link con predicciones pre-cargadas

### 4. Visualización de Datos
- Heatmap de predicciones por fuente
- Sparklines de accuracy por fecha
- Badges de "streak" (racha de aciertos)

## Implementación

```javascript
// Agregar al HTML existente

// 1. Modo oscuro
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// 2. Notificaciones de lesiones
function showInjuryAlert(player, team, match) {
  const alert = document.createElement('div');
  alert.className = 'injury-alert';
  alert.innerHTML = `
    <strong>${player}</strong> (${team}) - Duda para ${match}
    <button onclick="recalculateMatch('${match}')">Recalcular</button>
  `;
  document.getElementById('alerts').appendChild(alert);
}

// 3. Exportar predicciones
function exportPredictions() {
  const data = matches.map(m => ({
    match: `${m.a} vs ${m.b}`,
    consensus: getConsensus(m.c, m.g, m.f, m.fs, m.esp, m.yh, m.t, m.e, m.cup).score,
    date: m.d,
    group: m.gr
  }));
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `prode-predictions-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
}
```

## CSS para Dark Mode
```css
.dark-mode {
  --bg: #0f172a;
  --card: #1e293b;
  --text: #f1f5f9;
  --text2: #94a3b8;
  --border: #334155;
}
```

## Output
- HTML actualizado con nuevas features
- CSS mejorado

## Métricas
- Lighthouse score: > 90
- Mobile usability: 100%
- Tiempo de carga: < 2s
