'use client';

import { useEffect, useRef } from 'react';
import { GraduationCap, Award, Briefcase } from 'lucide-react';

export default function Beat2Identity() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      gsap.fromTo(
        sectionRef.current.querySelector('h2'),
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

      const textElements = sectionRef.current.querySelectorAll('.reveal-text');
      textElements.forEach((el: Element, idx: number) => {
        gsap.fromTo(
          el,
          { opacity: 0, y: 20 },
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

  return (
    <section
      ref={sectionRef}
      className="py-16 px-6 md:px-8 border-t border-white/5"
    >
      <div className="max-w-5xl w-full">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-8">
          Sobre mí
        </h2>

        <div className="reveal-text mb-12 p-6 rounded-lg border border-white/5 bg-white/[0.02]">
          <p className="text-lg md:text-xl text-gray-300 leading-relaxed">
            Estudiante de <span className="text-cyan font-semibold">Gestión de Tecnología de la Información</span> en UADE.
            Busco mi primera oportunidad como <span className="text-cyan font-semibold">Trainee/Junior</span> en Python, Web3 o análisis de datos.
            Construyo con IA como leverage — mi sistema de agentes con 44 workflows, 17 agentes y 78 skills me permite iterar 10x más rápido.
          </p>
        </div>

        {/* Three columns: Experience, Education, Certifications */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Experience */}
          <div className="reveal-text p-5 rounded-lg border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-2 mb-4">
              <Briefcase size={16} className="text-cyan" />
              <h3 className="text-sm font-mono text-gray-500 uppercase tracking-wider">Experiencia</h3>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-semibold text-gray-200">Grido | Atención y Gestión</p>
                <p className="text-xs text-gray-500 font-mono">2023 — Presente</p>
                <p className="text-xs text-gray-400 mt-1">Atención al cliente, gestión de caja y turnos. Control de stock.</p>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-200">Editor Multimedia Freelance</p>
                <p className="text-xs text-gray-500 font-mono">2021 — 2023</p>
                <p className="text-xs text-gray-400 mt-1">Edición en DaVinci Resolve para YouTube y TikTok.</p>
              </div>
            </div>
          </div>

          {/* Education */}
          <div className="reveal-text p-5 rounded-lg border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-2 mb-4">
              <GraduationCap size={16} className="text-cyan" />
              <h3 className="text-sm font-mono text-gray-500 uppercase tracking-wider">Educación</h3>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-semibold text-gray-200">UADE</p>
                <p className="text-xs text-gray-500 font-mono">2022 — Presente</p>
                <p className="text-xs text-gray-400 mt-1">Gestión de Tecnología de la Información</p>
              </div>
            </div>
          </div>

          {/* Certifications */}
          <div className="reveal-text p-5 rounded-lg border border-white/5 bg-white/[0.02]">
            <div className="flex items-center gap-2 mb-4">
              <Award size={16} className="text-cyan" />
              <h3 className="text-sm font-mono text-gray-500 uppercase tracking-wider">Certificaciones</h3>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-semibold text-gray-200">🐧 Red Hat System Administrator</p>
                <p className="text-xs text-gray-400 mt-1">Linux · Bash · Administración</p>
                <a
                  href="https://www.credly.com/badges/761f7f8d-41c7-4e1e-8dda-1e29830e4e85"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] text-cyan hover:underline font-mono"
                >
                  Ver credencial →
                </a>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-200">🤖 Claude Code in Action</p>
                <p className="text-xs text-gray-400 mt-1">AI Tools · Desarrollo con IA</p>
                <a
                  href="http://verify.skilljar.com/c/tco79gkq8a9k"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] text-cyan hover:underline font-mono"
                >
                  Ver credencial →
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
