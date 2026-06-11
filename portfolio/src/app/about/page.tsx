'use client';

import { useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import { Mail, Github, Linkedin, MapPin, GraduationCap } from 'lucide-react';

const timeline = [
  { year: '2026', title: 'AI Builder', description: 'Construyendo sistemas de agentes autónomos. 44 workflows, 17 agentes, 78 skills.' },
  { year: '2025', title: 'Full-Stack + AI', description: 'Next.js, FastAPI, Claude API. Productos end-to-end con IA como leverage.' },
  { year: '2024', title: 'Python & Automation', description: 'Automatización con Python, APIs, bots de Telegram. Primeros agentes.' },
  { year: '2023', title: 'Red Hat RH124', description: 'Certificación Red Hat. Linux, infraestructura, scripting.' },
  { year: '2022', title: 'Inicio en UADE', description: 'Gestión de Tecnología de la Información. Fundamentos de sistemas.' },
];

export default function AboutPage() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      const items = sectionRef.current.querySelectorAll('[data-timeline]');
      items.forEach((item: Element, idx: number) => {
        gsap.fromTo(
          item,
          { opacity: 0, x: -20 },
          {
            opacity: 1,
            x: 0,
            duration: 0.6,
            delay: idx * 0.1,
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
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan/20 bg-cyan/5 mb-6">
              <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
              <span className="text-cyan text-xs font-mono">whoami</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-space font-bold mb-4">
              <span className="bg-gradient-to-r from-cyan via-white to-accent bg-clip-text text-transparent">
                About
              </span>
            </h1>
            <p className="text-lg text-gray-400 max-w-xl font-mono">
              {'>'} Nacho Palmeri · Builder obsesionado con IA y automatización
            </p>
          </div>

          {/* Bio */}
          <div className="mb-16 p-6 rounded-lg border border-white/5 bg-white/[0.02]">
            <p className="text-gray-300 leading-relaxed mb-4">
              Soy un builder que usa IA como leverage para iterar más rápido. Mi sistema de agentes
              con <span className="text-cyan">44 workflows</span>, <span className="text-cyan">17 agentes</span> y <span className="text-cyan">78 skills</span> es mi superpoder: me permite
              automatizar, escalar y construir productos end-to-end con velocidad.
            </p>
            <p className="text-gray-400 leading-relaxed">
              Construyo con Next.js, Python, FastAPI y Claude API. Me interesa todo lo que tenga
              que ver con agentes autónomos, automatización inteligente y productos que usen IA
              como ventaja competitiva real.
            </p>
          </div>

          {/* Quick Facts */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
            {[
              { icon: MapPin, label: 'Buenos Aires', sublabel: 'Argentina' },
              { icon: GraduationCap, label: 'UADE', sublabel: 'Gestión de TI' },
              { icon: Mail, label: 'ignaciopalmeri1@gmail.com', sublabel: 'email' },
              { icon: Linkedin, label: '/in/ignaciopalmeri', sublabel: 'linkedin' },
            ].map(({ icon: Icon, label, sublabel }) => (
              <div key={label} className="p-4 rounded-lg border border-white/5 bg-white/[0.02]">
                <Icon size={16} className="text-cyan mb-2" />
                <div className="text-sm text-gray-200 font-mono">{label}</div>
                <div className="text-[10px] text-gray-600 font-mono">{sublabel}</div>
              </div>
            ))}
          </div>

          {/* Timeline */}
          <div className="mb-16">
            <h2 className="text-sm font-mono text-gray-500 mb-6 uppercase tracking-wider">Timeline</h2>
            <div className="space-y-0">
              {timeline.map((item) => (
                <div
                  key={item.year}
                  data-timeline={item.year}
                  className="group flex gap-6 py-4 border-l border-white/5 pl-6 hover:border-cyan/30 transition-colors"
                >
                  <span className="text-sm font-mono text-cyan w-12 shrink-0">{item.year}</span>
                  <div>
                    <h3 className="text-sm font-mono font-bold text-gray-200 group-hover:text-white transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-xs text-gray-500 leading-relaxed mt-1">
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Links */}
          <div className="flex gap-3">
            <a
              href="https://github.com/nachopalmeri"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-md bg-cyan/10 text-cyan border border-cyan/20 hover:bg-cyan hover:text-dark transition-all text-xs font-mono"
            >
              <Github size={14} />
              GitHub
            </a>
            <a
              href="https://linkedin.com/in/ignaciopalmeri"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-md border border-white/10 text-gray-400 hover:border-cyan/30 hover:text-cyan transition-all text-xs font-mono"
            >
              <Linkedin size={14} />
              LinkedIn
            </a>
            <a
              href="mailto:ignaciopalmeri1@gmail.com"
              className="flex items-center gap-2 px-4 py-2 rounded-md border border-white/10 text-gray-400 hover:border-cyan/30 hover:text-cyan transition-all text-xs font-mono"
            >
              <Mail size={14} />
              Email
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
