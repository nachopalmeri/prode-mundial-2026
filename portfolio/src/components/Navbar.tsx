'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X, Terminal } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / totalHeight) * 100;
      setScrollProgress(progress);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className="fixed top-0 w-full z-50">
      {/* Progress bar */}
      <div className="h-[2px] bg-[#0a0a0a]">
        <div
          className="h-full bg-gradient-to-r from-cyan to-accent transition-all duration-150"
          style={{ width: `${scrollProgress}%` }}
        />
      </div>

      <div className="backdrop-blur-xl bg-[#0a0a0a]/70 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              <Terminal size={18} className="text-cyan group-hover:rotate-12 transition-transform" />
              <span className="text-lg font-space font-bold bg-gradient-to-r from-cyan to-white bg-clip-text text-transparent">
                NP
              </span>
              <span className="hidden sm:inline text-xs font-mono text-gray-500">v2.0</span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-1">
              {[
                { href: '/', label: 'Home' },
                { href: '/projects', label: 'Projects' },
                { href: '/agents', label: 'Agents' },
                { href: '/stack', label: 'Stack' },
                { href: '/about', label: 'About' },
              ].map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className="px-3 py-1.5 text-sm text-gray-400 hover:text-cyan transition-colors rounded-md hover:bg-cyan/5"
                >
                  {label}
                </Link>
              ))}
            </div>

            {/* CTA */}
            <div className="hidden md:flex items-center gap-3">
              <a
                href="mailto:ignaciopalmeri1@gmail.com"
                className="text-xs px-4 py-1.5 rounded-md bg-cyan/10 text-cyan border border-cyan/20 hover:bg-cyan hover:text-dark transition-all font-semibold"
              >
                Contact
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-cyan transition-colors"
            >
              {isOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isOpen && (
            <div className="md:hidden pb-4 border-t border-white/5">
              {[
                { href: '/', label: 'Home' },
                { href: '/projects', label: 'Projects' },
                { href: '/agents', label: 'Agents' },
                { href: '/stack', label: 'Stack' },
                { href: '/about', label: 'About' },
              ].map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setIsOpen(false)}
                  className="block py-2.5 text-sm text-gray-400 hover:text-cyan transition-colors"
                >
                  {label}
                </Link>
              ))}
              <a
                href="mailto:ignaciopalmeri1@gmail.com"
                className="block mt-3 text-xs px-4 py-2 rounded-md bg-cyan/10 text-cyan border border-cyan/20 text-center font-semibold"
              >
                Contact
              </a>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
