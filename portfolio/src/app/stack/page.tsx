'use client';

import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';

const techCategories = [
  {
    name: 'Frontend',
    items: [
      { name: 'Next.js', level: 90, type: 'core' },
      { name: 'React', level: 90, type: 'core' },
      { name: 'TypeScript', level: 85, type: 'core' },
      { name: 'Tailwind CSS', level: 90, type: 'core' },
      { name: 'React Three Fiber', level: 70, type: 'specialized' },
      { name: 'Three.js', level: 65, type: 'specialized' },
      { name: 'GSAP', level: 75, type: 'specialized' },
      { name: 'Framer Motion', level: 80, type: 'core' },
    ],
  },
  {
    name: 'Backend',
    items: [
      { name: 'Python', level: 85, type: 'core' },
      { name: 'FastAPI', level: 80, type: 'core' },
      { name: 'PostgreSQL', level: 75, type: 'core' },
      { name: 'Supabase', level: 70, type: 'specialized' },
      { name: 'Alembic', level: 70, type: 'specialized' },
      { name: 'Pytest', level: 75, type: 'core' },
    ],
  },
  {
    name: 'AI / Agents',
    items: [
      { name: 'Claude API', level: 90, type: 'core' },
      { name: 'LangChain', level: 60, type: 'learning' },
      { name: 'Prompt Engineering', level: 90, type: 'core' },
      { name: 'RAG', level: 65, type: 'learning' },
      { name: 'Agent Orchestration', level: 85, type: 'core' },
    ],
  },
  {
    name: 'DevOps / Tools',
    items: [
      { name: 'Git / GitHub', level: 85, type: 'core' },
      { name: 'Vercel', level: 80, type: 'core' },
      { name: 'Docker', level: 65, type: 'learning' },
      { name: 'Railway', level: 70, type: 'specialized' },
      { name: 'CI/CD', level: 70, type: 'specialized' },
    ],
  },
];

const typeColors: Record<string, string> = {
  core: 'bg-cyan/10 text-cyan border-cyan/20',
  specialized: 'bg-accent/10 text-accent border-accent/20',
  learning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
};

export default function StackPage() {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      const items = sectionRef.current.querySelectorAll('[data-tech]');
      items.forEach((item: Element, idx: number) => {
        gsap.fromTo(
          item,
          { opacity: 0, y: 15 },
          {
            opacity: 1,
            y: 0,
            duration: 0.5,
            delay: idx * 0.04,
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
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <main ref={sectionRef} className="pt-24 pb-20 px-4">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan/20 bg-cyan/5 mb-6">
              <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
              <span className="text-cyan text-xs font-mono">tech radar</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-space font-bold mb-4">
              <span className="bg-gradient-to-r from-cyan via-white to-accent bg-clip-text text-transparent">
                Stack
              </span>
            </h1>
            <p className="text-lg text-gray-400 max-w-xl font-mono">
              {'>'} Herramientas que uso para construir, automatizar y escalar
            </p>
          </div>

          {/* Legend */}
          <div className="flex gap-4 mb-10">
            {Object.entries(typeColors).map(([type, classes]) => (
              <div key={type} className="flex items-center gap-2">
                <span className={`text-[10px] px-2 py-0.5 rounded border ${classes} font-mono`}>
                  {type}
                </span>
              </div>
            ))}
          </div>

          {/* Categories */}
          <div className="space-y-12">
            {techCategories.map((category) => (
              <div key={category.name}>
                <h2 className="text-sm font-mono text-gray-500 mb-4 uppercase tracking-wider">
                  {category.name}
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {category.items.map((tech) => (
                    <div
                      key={tech.name}
                      data-tech={tech.name}
                      onMouseEnter={() => setHoveredItem(tech.name)}
                      onMouseLeave={() => setHoveredItem(null)}
                      className={`group p-4 rounded-lg border transition-all cursor-default ${
                        hoveredItem === tech.name
                          ? 'border-cyan/30 bg-cyan/[0.03]'
                          : 'border-white/5 bg-white/[0.02]'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-mono text-gray-200 group-hover:text-white transition-colors">
                          {tech.name}
                        </span>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded border ${typeColors[tech.type]} font-mono`}>
                          {tech.type}
                        </span>
                      </div>
                      {/* Skill bar */}
                      <div className="h-1 rounded-full bg-white/5 overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-cyan to-accent transition-all duration-500"
                          style={{ width: hoveredItem === tech.name ? `${tech.level}%` : '0%' }}
                        />
                      </div>
                      {hoveredItem === tech.name && (
                        <div className="text-[10px] text-gray-500 font-mono mt-1.5">
                          proficiency: {tech.level}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
