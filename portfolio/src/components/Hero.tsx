'use client';

import { useEffect, useRef, Suspense } from 'react';
import { ArrowDown, Terminal } from 'lucide-react';
import dynamic from 'next/dynamic';

const NeuralNetwork3D = dynamic(() => import('@/components/3d/NeuralNetwork3D'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-dark" />,
});

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current) {
        const scrollY = window.scrollY;
        const opacity = Math.max(1 - scrollY / 600, 0);
        containerRef.current.style.opacity = opacity.toString();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <section
        ref={containerRef}
        className="relative h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0a]"
      >
        {/* 3D Neural Network Background */}
        <div className="absolute inset-0 z-0" data-3d-cursor>
          <Suspense fallback={<div className="w-full h-full bg-[#0a0a0a]" />}>
            <NeuralNetwork3D />
          </Suspense>
          {/* Gradient overlay for readability */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0a]/40 via-transparent to-[#0a0a0a]/80" />
        </div>

        {/* Scanline effect */}
        <div className="absolute inset-0 z-[1] pointer-events-none opacity-[0.03]"
          style={{ backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,217,255,0.03) 2px, rgba(0,217,255,0.03) 4px)' }}
        />

        {/* Content Overlay */}
        <div className="relative z-10 text-center px-4 max-w-5xl">
          {/* Terminal-style badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan/30 bg-cyan/5 mb-8">
            <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
            <span className="text-cyan text-sm font-mono">44 workflows · 17 agents · 78 skills</span>
          </div>

          <h1 className="text-5xl md:text-8xl font-space font-bold mb-6">
            <span className="bg-gradient-to-r from-cyan via-white to-accent bg-clip-text text-transparent">
              Nacho Palmeri
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 mb-4 font-light max-w-2xl mx-auto">
            Estudiante de Gestión IT buscando Trainee/Junior en Python, Web3 & Datos
          </p>
          <p className="text-base md:text-lg text-cyan/80 mb-12 font-mono">
            {'>'} Full-stack builder · Agent systems · Next.js + Python + Claude API
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <a
              href="#projects"
              className="px-8 py-3.5 rounded-lg bg-cyan text-dark font-semibold hover:bg-cyan/90 transition-all flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-cyan/20"
            >
              Ver Proyectos
            </a>
            <a
              href="#terminal"
              className="group px-8 py-3.5 rounded-lg border border-cyan/40 text-cyan hover:bg-cyan/10 hover:border-cyan transition-all font-semibold flex items-center justify-center gap-2"
            >
              <Terminal size={18} className="group-hover:rotate-12 transition-transform" />
              Terminal
            </a>
            <a
              href="mailto:ignaciopalmeri1@gmail.com"
              className="px-8 py-3.5 rounded-lg border border-white/20 text-gray-300 hover:border-cyan/30 hover:text-cyan transition-all font-semibold flex items-center justify-center gap-2"
            >
              Contacto
            </a>
          </div>

          <a
            href="#projects"
            className="text-sm text-gray-500 hover:text-cyan transition-colors font-mono"
          >
            scroll to explore ↓
          </a>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <ArrowDown className="text-cyan/50" size={20} />
        </div>
      </section>
    </>
  );
}
