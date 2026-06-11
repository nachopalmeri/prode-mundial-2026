# Multiagent Orchestration Plan — Portfolio Phases 3-6

## Estructura de Agentes Paralelos

```
┌─────────────────────────────────────────────────────────┐
│         agente-principal (Orquestador)                   │
│  Lógica, rutas, integraciones, síntesis final           │
└──────────────┬──────────────────────────────────────────┘
               │
      ┌────────┼────────┬──────────┬──────────┐
      │        │        │          │          │
      ▼        ▼        ▼          ▼          ▼
┌──────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ agente-  │ │agente│ │agente- │ │agente- │ │agente- │
│ design   │ │-seo  │ │tests   │ │docs    │ │ai-arch │
│          │ │      │ │        │ │        │ │        │
│UI/CSS/   │ │SEO   │ │E2E/    │ │Docs/   │ │RAG/    │
│Responsive│ │Perf  │ │Validar │ │README  │ │AI      │
└──────────┘ └──────┘ └────────┘ └────────┘ └────────┘
```

## Fases y Tareas por Agente

### ✅ Fase 3: Projects Page (COMPLETADA)

#### agente-principal
- [x] Crear `/projects` layout con grid dinámico
- [x] Definir estructura de datos (projects array con 4 proyectos)
- [x] Integrar con componentes de otros agentes
- [x] Scroll animations en project cards

#### agente-design
- [x] Diseñar project cards (layout, hover, mobile)
- [x] Crear filtro UI por tech stack (8 tecnologías)
- [x] Scroll animations para project cards
- [x] Responsive grid (1 col mobile, 2 tablet)

#### agente-seo
- [ ] Meta tags dinámicos por proyecto
- [ ] Schema.org para projects
- [ ] Open Graph para compartir

#### agente-tests
- [ ] E2E: Cargar página, filtrar, navegar a repos
- [ ] Validar que todos los links funcionan
- [ ] Performance: LCP < 2.5s, CLS < 0.1

#### agente-docs
- [x] Documentar estructura de projects data
- [ ] Guía para agregar nuevo proyecto

### ✅ Fase 4: Neural Command Center (COMPLETADA)

#### agente-principal
- [x] Implementar tabs funcionales (Agentes, Workflows, Skills)
- [x] Búsqueda global de agentes/workflows/skills
- [x] Filtrado dinámico en tiempo real

#### agente-design
- [x] Diseño de tabs y cards
- [x] Search bar con icono
- [x] Responsive layout para mobile

#### agente-seo
- [x] Meta tags para /agents
- [ ] Structured data para agentes

#### agente-tests
- [ ] Tab switching funciona
- [ ] Búsqueda filtra correctamente
- [ ] Mobile responsive

#### agente-docs
- [x] Documentar datos de agentes
- [ ] Guía de actualización

### Fase 5: Bilingual + Polish (Secuencial)

#### agente-principal
- [ ] Integrar next-intl
- [ ] Crear i18n config
- [ ] Traducir contenido

#### agente-design
- [ ] Language toggle en Navbar
- [ ] RTL support si aplica

#### agente-seo
- [ ] hreflang tags
- [ ] Sitemap multiidioma

#### agente-tests
- [ ] Cambio de idioma funciona
- [ ] Contenido traduce correctamente

### Fase 6: Performance & Deploy

#### agente-seo
- [ ] Lighthouse audit
- [ ] Optimizaciones de imagen
- [ ] Code splitting

#### agente-tests
- [ ] Lighthouse > 95 (Performance, SEO, Accessibility)
- [ ] E2E completo

#### agente-principal
- [ ] Build production
- [ ] Deploy a Vercel
- [ ] Domain setup

## Reglas de Integración

1. **Sin overlaps**: Cada agente toca su dominio
2. **Archivos esperados**:
   - agente-design: `src/components/`, `src/app/globals.css`
   - agente-principal: `src/app/`, rutas
   - agente-seo: `next.config.js`, metadata
   - agente-tests: `e2e/`, `__tests__/`
   - agente-docs: `README.md`, `docs/`

3. **Validación antes de merge**:
   - Cada agente valida su output
   - agente-principal sintetiza y decide
   - agente-tests verifica todo

4. **Criterio de salida**:
   - Fase 3: Projects page funcional + tests verdes
   - Fase 4: Neural Command Center interactivo + tests
   - Fase 5: Bilingual funcional + tests
   - Fase 6: Lighthouse > 95 + Deploy exitoso

## Worktrees (Opcional)

Si hay conflictos de edición:
```bash
git worktree add ../portfolio-design feature/design
git worktree add ../portfolio-seo feature/seo
git worktree add ../portfolio-tests feature/tests
```

## Comunicación

- **Checkpoint**: Cada agente reporta estado en su sección
- **Bloqueos**: Reportar inmediatamente al agente-principal
- **Cambios de scope**: Pedir confirmación antes de editar

## Próxima Acción

1. **agente-principal**: Crear estructura de `/projects`
2. **agente-design**: Diseñar project cards en paralelo
3. **agente-seo**: Preparar meta tags
4. **agente-tests**: Escribir tests E2E
5. **agente-docs**: Documentar estructura

---

**Orquestador**: agente-principal  
**Validador**: agente-tests  
**Síntesis**: agente-principal + agente-tests
