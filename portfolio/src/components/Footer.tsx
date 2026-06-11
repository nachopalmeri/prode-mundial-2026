'use client';

import { Github, Linkedin, Mail, Terminal } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#0a0a0a]">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Terminal size={16} className="text-cyan" />
              <span className="text-lg font-space font-bold bg-gradient-to-r from-cyan to-white bg-clip-text text-transparent">
                NP
              </span>
            </div>
            <p className="text-sm text-gray-600 font-mono max-w-xs">
              {'>'} Builder obsesionado con IA, sistemas autónomos y automatización.
            </p>
          </div>

          {/* Nav */}
          <div className="grid grid-cols-2 gap-x-12 gap-y-2 text-sm font-mono">
            <a href="/" className="text-gray-500 hover:text-cyan transition-colors">Home</a>
            <a href="/agents" className="text-gray-500 hover:text-cyan transition-colors">Agents</a>
            <a href="/projects" className="text-gray-500 hover:text-cyan transition-colors">Projects</a>
            <a href="/stack" className="text-gray-500 hover:text-cyan transition-colors">Stack</a>
            <a href="/about" className="text-gray-500 hover:text-cyan transition-colors">About</a>
            <a href="#contact" className="text-gray-500 hover:text-cyan transition-colors">Contact</a>
          </div>

          {/* Social */}
          <div className="flex gap-3">
            <a
              href="https://github.com/nachopalmeri"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-md border border-white/5 text-gray-500 hover:text-cyan hover:border-cyan/30 transition-all"
            >
              <Github size={16} />
            </a>
            <a
              href="https://linkedin.com/in/ignaciopalmeri"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-md border border-white/5 text-gray-500 hover:text-cyan hover:border-cyan/30 transition-all"
            >
              <Linkedin size={16} />
            </a>
            <a
              href="mailto:ignaciopalmeri1@gmail.com"
              className="p-2 rounded-md border border-white/5 text-gray-500 hover:text-cyan hover:border-cyan/30 transition-all"
            >
              <Mail size={16} />
            </a>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-2">
          <p className="text-xs text-gray-700 font-mono">
            © 2026 Nacho Palmeri · Built with Next.js + R3F + GSAP
          </p>
          <p className="text-xs text-gray-700 font-mono">
            44 workflows · 17 agents · 78 skills
          </p>
        </div>
      </div>
    </footer>
  );
}
