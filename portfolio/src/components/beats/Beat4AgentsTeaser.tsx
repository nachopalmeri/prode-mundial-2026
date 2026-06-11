'use client';

import { useEffect, useRef } from 'react';

export default function Beat4AgentsTeaser() {
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

      const stats = sectionRef.current.querySelectorAll('[data-stat]');
      stats.forEach((stat: Element, idx: number) => {
        gsap.fromTo(
          stat,
          { opacity: 0, scale: 0.9 },
          {
            opacity: 1,
            scale: 1,
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
    <section ref={sectionRef} className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl w-full text-center">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-8">
          Neural Command Center
        </h2>

        <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
          10 agents. 8 core workflows. 78 reusable skills. This isn&apos;t a demo — it&apos;s my actual development system, running every day.
        </p>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div data-stat="workflows" className="p-6 rounded-lg border border-white/5 hover:border-cyan/40 transition-colors bg-white/[0.02]">
            <div className="text-3xl font-space font-bold text-cyan mb-2">44</div>
            <p className="text-sm text-gray-500 font-mono">workflows</p>
          </div>
          <div data-stat="agents" className="p-6 rounded-lg border border-white/5 hover:border-cyan/40 transition-colors bg-white/[0.02]">
            <div className="text-3xl font-space font-bold text-cyan mb-2">17</div>
            <p className="text-sm text-gray-500 font-mono">agents</p>
          </div>
          <div data-stat="skills" className="p-6 rounded-lg border border-white/5 hover:border-cyan/40 transition-colors bg-white/[0.02]">
            <div className="text-3xl font-space font-bold text-cyan mb-2">78</div>
            <p className="text-sm text-gray-500 font-mono">skills</p>
          </div>
        </div>

        <a
          href="/agents"
          className="inline-block px-8 py-3 rounded-md bg-cyan/10 text-cyan border border-cyan/20 hover:bg-cyan hover:text-dark transition-all font-semibold font-mono text-sm"
        >
          {'>'} Explorar el sistema completo
        </a>
      </div>
    </section>
  );
}
