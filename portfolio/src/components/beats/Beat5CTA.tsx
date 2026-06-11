'use client';

import { useEffect, useRef } from 'react';
import { Mail, Github, Linkedin } from 'lucide-react';

export default function Beat5CTA() {
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

      const buttons = sectionRef.current.querySelectorAll('[data-cta]');
      buttons.forEach((btn: Element, idx: number) => {
        gsap.fromTo(
          btn,
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
    <section ref={sectionRef} id="contact" className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl w-full">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-8">
          Contacto
        </h2>

        <p className="text-gray-400 mb-8 max-w-md">
          Busco mi primera oportunidad como Trainee/Junior en Python, Web3 o datos. Si tu equipo necesita alguien que construye con IA, hablemos.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <a
            data-cta="email"
            href="mailto:ignaciopalmeri1@gmail.com"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white text-black font-medium hover:bg-gray-200 transition-colors"
          >
            <Mail size={16} />
            Email
          </a>
          <a
            data-cta="linkedin"
            href="https://linkedin.com/in/ignaciopalmeri"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-white/20 text-gray-300 hover:border-white/40 transition-colors font-medium"
          >
            <Linkedin size={16} />
            LinkedIn
          </a>
          <a
            data-cta="github"
            href="https://github.com/nachopalmeri"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-white/20 text-gray-300 hover:border-white/40 transition-colors font-medium"
          >
            <Github size={16} />
            GitHub
          </a>
        </div>

        <a
          href="mailto:ignaciopalmeri1@gmail.com"
          className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors group"
        >
          <span>Hablemos</span>
          <span className="group-hover:translate-x-1 transition-transform duration-200">→</span>
        </a>
      </div>
    </section>
  );
}
