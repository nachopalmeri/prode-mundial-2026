'use client';

import { useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import Beat2Identity from '@/components/beats/Beat2Identity';
import Beat3Ecosystem from '@/components/beats/Beat3Ecosystem';
import Certifications from '@/components/beats/Certifications';
import GitHubActivity from '@/components/beats/GitHubActivity';
import TerminalSection from '@/components/beats/TerminalSection';
import Beat4AgentsTeaser from '@/components/beats/Beat4AgentsTeaser';
import Beat5CTA from '@/components/beats/Beat5CTA';
import Footer from '@/components/Footer';

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    // Refresh ScrollTrigger after 3D loads
    const timer = setTimeout(() => ScrollTrigger.refresh(), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div ref={containerRef} className="min-h-screen bg-[#0a0a0a] overflow-x-hidden">
      <Navbar />
      <main className="relative">
        <Hero />
        <Beat2Identity />
        <Beat3Ecosystem />
        <Certifications />
        <GitHubActivity />
        <TerminalSection />
        <Beat4AgentsTeaser />
        <Beat5CTA />
      </main>
      <Footer />
    </div>
  );
}
