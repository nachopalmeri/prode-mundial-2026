'use client';

import { useState, useEffect, useRef, Suspense } from 'react';
import dynamic from 'next/dynamic';
import Navbar from '@/components/Navbar';
import { Search, Terminal, Activity, Cpu, Zap } from 'lucide-react';

const AgentSystemViz = dynamic(() => import('@/components/3d/AgentSystemViz'), {
  ssr: false,
  loading: () => <div className="w-full h-[500px] bg-[#0a0a0a] rounded-lg border border-white/5 flex items-center justify-center text-gray-600 font-mono text-sm">Loading 3D visualization...</div>,
});

export default function AgentsPage() {
  const [selectedCategory, setSelectedCategory] = useState<'agents' | 'workflows' | 'skills'>('agents');
  const [searchQuery, setSearchQuery] = useState('');
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    if (sectionRef.current) {
      gsap.fromTo(
        sectionRef.current.querySelector('h1'),
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

      const items = sectionRef.current.querySelectorAll('[data-item]');
      items.forEach((item: Element, idx: number) => {
        gsap.fromTo(
          item,
          { opacity: 0, y: 20 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            delay: idx * 0.08,
            scrollTrigger: {
              trigger: sectionRef.current,
              start: 'top 70%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      });
    }
  }, [selectedCategory]);

  const agents = [
    { name: 'agente-principal', description: 'Lógica, estructura, integraciones, APIs', status: 'active', icon: Cpu },
    { name: 'agente-design', description: 'CSS, responsive, animaciones, accesibilidad', status: 'active', icon: Zap },
    { name: 'agente-web-3d', description: 'Three.js, R3F, Spline, shaders, WebGPU', status: 'active', icon: Activity },
    { name: 'agente-web-motion', description: 'GSAP, ScrollTrigger, Lenis, micro-interacciones', status: 'active', icon: Activity },
    { name: 'agente-web-copy', description: 'Copy persuasivo, CTAs, storytelling', status: 'active', icon: Terminal },
    { name: 'agente-web-qa', description: 'Lighthouse, anti-slop, accesibilidad, performance', status: 'active', icon: Activity },
    { name: 'agente-marketing-strategist', description: 'Estrategia, posicionamiento, GTM', status: 'standby', icon: Terminal },
    { name: 'agente-growth-seo-geo', description: 'SEO/GEO growth, keywords, backlinks', status: 'standby', icon: Activity },
    { name: 'agente-security-auditor', description: 'Secretos, permisos, supply-chain security', status: 'standby', icon: Cpu },
    { name: 'agente-obsidian-brain', description: 'Obsidian vault, notas, MOCs, Dataview', status: 'standby', icon: Terminal },
  ];

  const workflows = [
    { name: 'web-factory', description: 'Orquestación tipo Lovable con 5 agentes sandboxed', category: 'build', agents: 5 },
    { name: 'world-class-web', description: 'Pipeline 10 etapas para web 3D inmersiva', category: 'build', agents: 5 },
    { name: 'spec_kit', description: 'Spec-driven development: constitution → spec → plan → tasks', category: 'plan', agents: 2 },
    { name: 'parallel_agents', description: 'Tareas independientes en paralelo con worktrees', category: 'execute', agents: 3 },
    { name: 'validation', description: 'Quality gate antes de declarar listo', category: 'verify', agents: 1 },
    { name: 'feedback_loop', description: 'Aprendizaje de errores en tiempo real', category: 'learn', agents: 1 },
    { name: 'multiagent_review_loop', description: 'Crear → criticar → red team → plan', category: 'review', agents: 3 },
    { name: 'venture_loop', description: 'Loop idea→MVP→landing→distribución→medición', category: 'business', agents: 2 },
  ];

  const skills = [
    { name: 'premium-web-stack', domain: 'web', description: 'Next.js + shadcn/ui + R3F + GSAP + Spline' },
    { name: 'brainstorming', domain: 'creative', description: 'Explorar intención antes de implementar' },
    { name: 'systematic-debugging', domain: 'debug', description: 'Root cause antes de implementar fixes' },
    { name: 'test-driven-development', domain: 'quality', description: 'Tests antes de implementación' },
    { name: 'writing-plans', domain: 'plan', description: 'Planes para tareas multi-step' },
    { name: 'dispatching-parallel-agents', domain: 'execute', description: '2+ tareas independientes en paralelo' },
    { name: 'verification-before-completion', domain: 'quality', description: 'Verificar antes de declarar listo' },
    { name: 'requesting-code-review', domain: 'quality', description: 'Code review antes de merge' },
    { name: 'frontend-design', domain: 'web', description: 'Interfaces production-grade con React' },
    { name: 'css-animations', domain: 'web', description: 'Animaciones CSS 2D: keyframes, parallax, hover' },
    { name: 'seo-geo-growth', domain: 'growth', description: 'SEO/GEO/AEO growth strategy' },
    { name: 'product-foundry', domain: 'business', description: 'Indie product ideation, MVP scoping' },
  ];

  const filteredAgents = agents.filter(a =>
    a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    a.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredWorkflows = workflows.filter(w =>
    w.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    w.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredSkills = skills.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />

      <main ref={sectionRef} className="pt-24 pb-20 px-4">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan/20 bg-cyan/5 mb-6">
              <span className="w-2 h-2 rounded-full bg-cyan animate-pulse" />
              <span className="text-cyan text-xs font-mono">system online</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-space font-bold mb-4">
              <span className="bg-gradient-to-r from-cyan via-white to-accent bg-clip-text text-transparent">
                Neural Command Center
              </span>
            </h1>
            <p className="text-lg text-gray-400 max-w-xl mx-auto font-mono">
              {'>'} 44 workflows · 17 agents · 78 skills
            </p>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-3 gap-4 mb-12 max-w-lg mx-auto">
            <div className="text-center p-3 rounded-lg border border-white/5 bg-white/[0.02]">
              <div className="text-2xl font-space font-bold text-cyan">44</div>
              <div className="text-xs text-gray-500 font-mono">workflows</div>
            </div>
            <div className="text-center p-3 rounded-lg border border-white/5 bg-white/[0.02]">
              <div className="text-2xl font-space font-bold text-cyan">17</div>
              <div className="text-xs text-gray-500 font-mono">agents</div>
            </div>
            <div className="text-center p-3 rounded-lg border border-white/5 bg-white/[0.02]">
              <div className="text-2xl font-space font-bold text-cyan">78</div>
              <div className="text-xs text-gray-500 font-mono">skills</div>
            </div>
          </div>

          {/* 3D Agent Graph */}
          <div className="mb-12" data-3d-cursor>
            <Suspense fallback={<div className="w-full h-[500px] bg-[#0a0a0a] rounded-lg border border-white/5" />}>
              <AgentSystemViz />
            </Suspense>
          </div>

          {/* Search Bar */}
          <div className="mb-10 max-w-xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-3 text-gray-500" size={18} />
              <input
                type="text"
                placeholder="Search agents, workflows, skills..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-lg bg-white/[0.03] border border-white/10 text-gray-200 placeholder-gray-600 focus:border-cyan/50 focus:outline-none transition-colors font-mono text-sm"
              />
            </div>
          </div>

          {/* Category Tabs */}
          <div className="flex gap-2 justify-center mb-10">
            {[
              { key: 'agents' as const, label: 'Agents', count: filteredAgents.length },
              { key: 'workflows' as const, label: 'Workflows', count: filteredWorkflows.length },
              { key: 'skills' as const, label: 'Skills', count: filteredSkills.length },
            ].map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-5 py-2 rounded-md text-sm font-mono transition-all ${
                  selectedCategory === key
                    ? 'bg-cyan/10 text-cyan border border-cyan/30'
                    : 'text-gray-500 hover:text-gray-300 border border-transparent'
                }`}
              >
                {label} <span className="text-xs opacity-50">({count})</span>
              </button>
            ))}
          </div>

          {/* Content */}
          {selectedCategory === 'agents' && (
            <div className="grid md:grid-cols-2 gap-4">
              {filteredAgents.length > 0 ? (
                filteredAgents.map((agent) => (
                  <div
                    key={agent.name}
                    data-item={agent.name}
                    className="group p-5 rounded-lg border border-white/5 hover:border-cyan/30 bg-white/[0.02] hover:bg-cyan/[0.03] transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-mono font-bold text-cyan group-hover:text-white transition-colors">
                        {'>'} {agent.name}
                      </h3>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono ${
                        agent.status === 'active'
                          ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                          : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                      }`}>
                        {agent.status}
                      </span>
                    </div>
                    <p className="text-gray-500 text-xs leading-relaxed">{agent.description}</p>
                  </div>
                ))
              ) : (
                <div className="col-span-2 text-center py-8">
                  <p className="text-gray-600 font-mono text-sm">No agents found.</p>
                </div>
              )}
            </div>
          )}

          {selectedCategory === 'workflows' && (
            <div className="grid md:grid-cols-2 gap-4">
              {filteredWorkflows.length > 0 ? (
                filteredWorkflows.map((workflow) => (
                  <div
                    key={workflow.name}
                    data-item={workflow.name}
                    className="group p-5 rounded-lg border border-white/5 hover:border-cyan/30 bg-white/[0.02] hover:bg-cyan/[0.03] transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-mono font-bold text-cyan group-hover:text-white transition-colors">
                        {'>'} {workflow.name}
                      </h3>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan/5 text-cyan/60 border border-cyan/10 font-mono">
                        {workflow.category}
                      </span>
                    </div>
                    <p className="text-gray-500 text-xs leading-relaxed mb-3">{workflow.description}</p>
                    <div className="text-[10px] text-gray-600 font-mono">
                      agents required: {workflow.agents}
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 text-center py-8">
                  <p className="text-gray-600 font-mono text-sm">No workflows found.</p>
                </div>
              )}
            </div>
          )}

          {selectedCategory === 'skills' && (
            <div className="grid md:grid-cols-3 gap-3">
              {filteredSkills.length > 0 ? (
                filteredSkills.map((skill) => (
                  <div
                    key={skill.name}
                    data-item={skill.name}
                    className="group p-4 rounded-lg border border-white/5 hover:border-cyan/30 bg-white/[0.02] hover:bg-cyan/[0.03] transition-all"
                  >
                    <div className="flex items-start justify-between mb-1">
                      <h3 className="text-xs font-mono font-bold text-cyan group-hover:text-white transition-colors">
                        {skill.name}
                      </h3>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-accent/5 text-accent/60 border border-accent/10 font-mono">
                        {skill.domain}
                      </span>
                    </div>
                    <p className="text-gray-600 text-[11px] leading-relaxed">{skill.description}</p>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-8">
                  <p className="text-gray-600 font-mono text-sm">No skills found.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
