# Portfolio — Nacho Palmeri

Portfolio web premium para Nacho Palmeri. Builder obsesionado con IA, sistemas autónomos y automatización.

## Stack

- **Framework:** Next.js 15 (App Router)
- **3D:** React Three Fiber + Three.js
- **Animaciones:** GSAP + ScrollTrigger
- **Estilos:** Tailwind CSS v4
- **Componentes:** shadcn/ui
- **Iconos:** Lucide React
- **Fonts:** Space Grotesk, Inter, JetBrains Mono

## Estructura

```
src/
├── app/
│   ├── page.tsx          # Homepage con 5 beats
│   ├── agents/           # Neural Command Center
│   ├── projects/         # Proyectos detallados
│   ├── stack/            # Tech stack
│   ├── about/            # Sobre mí
│   ├── layout.tsx        # Layout global
│   └── globals.css       # Estilos globales
├── components/
│   ├── Navbar.tsx
│   ├── Hero.tsx
│   ├── beats/            # Secciones de scroll
│   └── 3d/               # Componentes 3D
```

## Desarrollo

```bash
npm install
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## Fases de Implementación

- [x] Fase 1: Setup + Hero
- [ ] Fase 2: Scroll Narrativo (completo)
- [ ] Fase 3: Projects
- [ ] Fase 4: Neural Command Center (completo)
- [ ] Fase 5: Stack + About + Contact
- [ ] Fase 6: Polish + Performance

## Deploy

```bash
npm run build
npm start
```

Deploy a Vercel: `vercel deploy`
