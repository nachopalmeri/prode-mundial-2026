'use client';

import { useEffect, useRef } from 'react';
import { ExternalLink } from 'lucide-react';

const certifications = [
  {
    title: 'Red Hat System Administrator',
    issuer: 'Red Hat',
    skills: ['Linux', 'Bash', 'Administración'],
    emoji: '🐧',
    link: 'https://www.credly.com/badges/761f7f8d-41c7-4e1e-8dda-1e29830e4e85',
  },
  {
    title: 'Claude Code in Action',
    issuer: 'Anthropic',
    skills: ['AI Tools', 'Desarrollo con IA'],
    emoji: '🤖',
    link: 'http://verify.skilljar.com/c/tco79gkq8a9k',
  },
];

export default function Certifications() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      const items = sectionRef.current.querySelectorAll('[data-cert]');
      items.forEach((item: Element, idx: number) => {
        gsap.fromTo(
          item,
          { opacity: 0, y: 20 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            delay: idx * 0.15,
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
    <section ref={sectionRef} className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-6">
          Certificaciones
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {certifications.map((cert) => (
            <div
              key={cert.title}
              data-cert={cert.title}
              className="group p-6 rounded-lg border border-white/5 hover:border-cyan/30 bg-white/[0.02] hover:bg-cyan/[0.03] transition-all duration-300"
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-4xl">{cert.emoji}</span>
                <a
                  href={cert.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-md border border-white/10 text-gray-500 hover:text-cyan hover:border-cyan/30 transition-all"
                >
                  <ExternalLink size={14} />
                </a>
              </div>
              <h3 className="text-lg font-space font-bold text-gray-200 group-hover:text-cyan transition-colors mb-1">
                {cert.title}
              </h3>
              <p className="text-xs text-gray-500 font-mono mb-3">{cert.issuer}</p>
              <div className="flex flex-wrap gap-1.5">
                {cert.skills.map((skill) => (
                  <span
                    key={skill}
                    className="text-[10px] px-2 py-0.5 rounded bg-cyan/5 text-cyan/70 border border-cyan/20 font-mono"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
