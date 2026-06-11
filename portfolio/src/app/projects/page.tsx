'use client';

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import TiltCard from '@/components/TiltCard';
import { ExternalLink, Github } from 'lucide-react';

const projects = [
  {
    id: 'pisculichi-labs',
    name: 'Pisculichi Labs',
    tagline: 'The Operating System for Prediction Markets',
    description: 'Plataforma para mercados de predicción. FillSense Bot, Alpha Feed y herramientas de análisis en tiempo real.',
    tech: ['Python', 'Telegram', 'Polymarket'],
    image: '📈',
    link: 'https://polytools-omega.vercel.app',
    github: 'https://github.com/nachopalmeri/pisculichi-labs',
    highlights: ['Prediction Markets', 'FillSense Bot', 'Alpha Feed'],
  },
  {
    id: 'agents-system',
    name: 'Agents System',
    tagline: 'Sistema portable de agentes con 44 workflows',
    description: 'Arquitectura modular para orquestar múltiples agentes autónomos. Incluye 44 workflows, 17 agentes especializados y 78 skills reutilizables.',
    tech: ['Python', 'YAML', 'TypeScript', 'Claude API'],
    image: '🤖',
    link: 'https://github.com/nachopalmeri/agents-system',
    github: 'https://github.com/nachopalmeri/agents-system',
    highlights: ['44 workflows', '17 agentes', '78 skills'],
  },
  {
    id: 'franquiya',
    name: 'Dashboard Franquiciados',
    tagline: 'Sistema integral de gestión para franquicias',
    description: 'Control de stock, plan de compra, turnos de empleados y reportes en tiempo real.',
    tech: ['Python', 'API', 'Dashboard'],
    image: '📊',
    link: 'https://franqui-ya.vercel.app',
    github: 'https://github.com/nachopalmeri/FranquiYA',
    highlights: ['Stock', 'Compras', 'Turnos'],
  },
  {
    id: 'pisku-cli',
    name: 'PISKU CLI',
    tagline: 'Context selector para LLMs',
    description: 'Selecciona archivos relevantes automáticamente para alimentar contexto de modelos de lenguaje.',
    tech: ['Python', 'CLI', 'AI'],
    image: '⚡',
    link: 'https://pisku-production.up.railway.app',
    github: 'https://github.com/nachopalmeri/pisku-cli',
    highlights: ['Auto-context', 'CLI tool', 'LLM-ready'],
  },
  {
    id: 'jobbot',
    name: 'Job Bot',
    tagline: 'Bot de Telegram para oportunidades laborales',
    description: 'Monitorea oportunidades laborales en tiempo real y las envía por Telegram.',
    tech: ['Python', 'Telegram'],
    image: '💼',
    link: 'https://job--bot.vercel.app',
    github: 'https://github.com/nachopalmeri/jobbot',
    highlights: ['Real-time', 'Telegram', 'Auto-monitor'],
  },
  {
    id: 'futbol-tracker',
    name: 'Fútbol Tracker',
    tagline: 'Estadísticas de fútbol amateur',
    description: 'Seguimiento de estadísticas de fútbol amateur con visualización de datos.',
    tech: ['HTML/CSS', 'JavaScript'],
    image: '⚽',
    link: 'https://fulbotracker.vercel.app',
    github: 'https://github.com/nachopalmeri/futbol-tracker',
    highlights: ['Stats', 'Visualización', 'Amateur'],
  },
  {
    id: 'comida-barrio',
    name: 'Comida de Barrio',
    tagline: 'E-commerce de restaurantes locales',
    description: 'Sistema de pedidos online para restaurantes de barrio con carrito y checkout.',
    tech: ['HTML/CSS', 'JavaScript', 'Bootstrap'],
    image: '�',
    link: 'https://comidadebarrio.vercel.app',
    github: 'https://github.com/nachopalmeri/comida-barrio',
    highlights: ['E-commerce', 'Pedidos', 'Local'],
  },
];

const techStack = ['Python', 'FastAPI', 'Next.js', 'PostgreSQL', 'TypeScript', 'Claude API', 'Telegram', 'CLI', 'AI', 'HTML/CSS', 'JavaScript', 'Bootstrap'];

export default function ProjectsPage() {
  const [selectedTech, setSelectedTech] = useState<string | null>(null);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      gsap.fromTo(
        sectionRef.current.querySelector('h1'),
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          scrollTrigger: {
            trigger: sectionRef.current,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      const cards = sectionRef.current.querySelectorAll('[data-project]');
      cards.forEach((card: Element, idx: number) => {
        gsap.fromTo(
          card,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: idx * 0.15,
            scrollTrigger: {
              trigger: sectionRef.current,
              start: 'top 70%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      });
    }
  }, []);

  const filteredProjects = selectedTech
    ? projects.filter(p => p.tech.includes(selectedTech))
    : projects;

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <main ref={sectionRef} className="pt-24 pb-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan/20 bg-cyan/5 mb-6">
              <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
              <span className="text-cyan text-xs font-mono">{filteredProjects.length} projects loaded</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-space font-bold mb-4">
              <span className="bg-gradient-to-r from-cyan via-white to-accent bg-clip-text text-transparent">
                Projects
              </span>
            </h1>
            <p className="text-lg text-gray-400 max-w-xl font-mono">
              {'>'} Ecosistema de productos con velocidad, IA y automatización
            </p>
          </div>

          {/* Tech Filter */}
          <div className="mb-16">
            <p className="text-xs text-gray-600 mb-3 font-mono">filter by tech:</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedTech(null)}
                className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all ${
                  selectedTech === null
                    ? 'bg-cyan/10 text-cyan border border-cyan/30'
                    : 'text-gray-500 hover:text-gray-300 border border-transparent'
                }`}
              >
                Todos
              </button>
              {techStack.map(tech => (
                <button
                  key={tech}
                  onClick={() => setSelectedTech(tech)}
                  className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all ${
                    selectedTech === tech
                      ? 'bg-cyan/10 text-cyan border border-cyan/30'
                      : 'text-gray-500 hover:text-gray-300 border border-transparent'
                  }`}
                >
                  {tech}
                </button>
              ))}
            </div>
          </div>

          {/* Projects Grid */}
          <div className="grid md:grid-cols-2 gap-8">
            {filteredProjects.map((project) => (
              <TiltCard
                key={project.id}
                data-project={project.id}
                className="group p-6 rounded-lg border border-white/5 hover:border-cyan/30 bg-white/[0.02] hover:bg-cyan/[0.03] transition-all duration-300"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{project.image}</span>
                    <div>
                      <h3 className="text-xl font-space font-bold text-cyan group-hover:text-white transition-colors">
                        {'>'} {project.name}
                      </h3>
                      <p className="text-sm text-gray-400">{project.tagline}</p>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p className="text-gray-300 text-sm mb-4 leading-relaxed">
                  {project.description}
                </p>

                {/* Highlights */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.highlights.map((highlight, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 rounded bg-cyan/5 text-cyan/80 border border-cyan/20"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>

                {/* Tech Stack */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {project.tech.map((tech, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 rounded bg-white/[0.03] text-gray-400 border border-white/5"
                    >
                      {tech}
                    </span>
                  ))}
                </div>

                {/* Links */}
                <div className="flex gap-3">
                  <a
                    href={project.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded-md bg-cyan/10 text-cyan hover:bg-cyan hover:text-dark transition-all text-xs font-mono"
                  >
                    <ExternalLink size={16} />
                    Ver
                  </a>
                  <a
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded-md border border-white/10 text-gray-400 hover:border-cyan/30 hover:text-cyan transition-all text-xs font-mono"
                  >
                    <Github size={16} />
                    Código
                  </a>
                </div>
              </TiltCard>
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-600 font-mono text-sm">No projects found for that tech.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
