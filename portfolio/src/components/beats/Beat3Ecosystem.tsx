'use client';

import { useEffect, useRef } from 'react';
import { ExternalLink } from 'lucide-react';

const projects = [
  {
    name: 'Pisculichi Labs',
    description: 'The Operating System for Prediction Markets. FillSense Bot, Alpha Feed y más.',
    tech: ['Python', 'Telegram', 'Polymarket'],
    year: '2025',
    link: 'https://polytools-omega.vercel.app',
    gradient: 'from-purple-900/40 to-cyan-900/40',
    emoji: '📈',
  },
  {
    name: 'Dashboard Franquiciados',
    description: 'Sistema integral de gestión: control de stock, plan de compra, turnos de empleados.',
    tech: ['Python', 'API', 'Dashboard'],
    year: '2025',
    link: 'https://franqui-ya.vercel.app',
    gradient: 'from-blue-900/40 to-emerald-900/40',
    emoji: '📊',
  },
  {
    name: 'Agents System',
    description: 'Sistema portable de agentes con 44 workflows, 17 agentes y 78 skills.',
    tech: ['Python', 'YAML', 'TypeScript', 'Claude API'],
    year: '2025',
    link: '/agents',
    gradient: 'from-cyan-900/40 to-violet-900/40',
    emoji: '🤖',
  },
  {
    name: 'PISKU CLI',
    description: 'Context selector para LLMs. Selecciona archivos relevantes automáticamente.',
    tech: ['Python', 'CLI', 'AI'],
    year: '2025',
    link: 'https://pisku-production.up.railway.app',
    gradient: 'from-amber-900/40 to-red-900/40',
    emoji: '⚡',
  },
  {
    name: 'Job Bot',
    description: 'Bot de Telegram que monitorea oportunidades laborales en tiempo real.',
    tech: ['Python', 'Telegram'],
    year: '2025',
    link: 'https://job--bot.vercel.app',
    gradient: 'from-green-900/40 to-teal-900/40',
    emoji: '💼',
  },
  {
    name: 'Fútbol Tracker',
    description: 'Seguimiento de estadísticas de fútbol amateur con visualización de datos.',
    tech: ['HTML/CSS', 'JavaScript'],
    year: '2024',
    link: 'https://fulbotracker.vercel.app',
    gradient: 'from-lime-900/40 to-green-900/40',
    emoji: '⚽',
  },
  {
    name: 'Comida de Barrio',
    description: 'E-commerce de restaurantes locales con sistema de pedidos online.',
    tech: ['HTML/CSS', 'JavaScript', 'Bootstrap'],
    year: '2024',
    link: 'https://comidadebarrio.vercel.app',
    gradient: 'from-orange-900/40 to-yellow-900/40',
    emoji: '🍔',
  },
];

export default function Beat3Ecosystem() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      const cards = sectionRef.current.querySelectorAll('[data-project]');
      cards.forEach((card: Element, idx: number) => {
        gsap.fromTo(
          card,
          { opacity: 0, y: 20 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            delay: idx * 0.08,
            scrollTrigger: {
              trigger: sectionRef.current,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      });
    }
  }, []);

  return (
    <section ref={sectionRef} id="projects" className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-8">Proyectos</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => {
            const isInternal = project.link.startsWith('/');
            const Tag = isInternal ? 'a' : 'a';
            const props = isInternal
              ? { href: project.link }
              : { href: project.link, target: '_blank' as const, rel: 'noopener noreferrer' };

            return (
              <Tag
                key={project.name}
                {...props}
                data-project={project.name}
                className="group block rounded-xl border border-white/5 hover:border-white/20 bg-[#0a0a0a] overflow-hidden transition-all duration-300 hover:-translate-y-1"
              >
                {/* Carátula */}
                <div className={`h-32 bg-gradient-to-br ${project.gradient} flex items-center justify-center relative`}>
                  <span className="text-5xl">{project.emoji}</span>
                  <span className="absolute top-3 right-3 text-[10px] text-gray-400 font-mono">{project.year}</span>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="text-base font-bold text-gray-200 group-hover:text-white transition-colors mb-2">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-500 leading-relaxed mb-4">
                    {project.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {project.tech.map((tech) => (
                      <span
                        key={tech}
                        className="px-2 py-0.5 text-[10px] text-gray-500 bg-white/5 rounded font-mono"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-600 group-hover:text-cyan font-mono transition-colors">
                    <ExternalLink size={12} />
                    {isInternal ? 'Ver en el sitio' : 'Ver proyecto'}
                  </div>
                </div>
              </Tag>
            );
          })}
        </div>
      </div>
    </section>
  );
}
