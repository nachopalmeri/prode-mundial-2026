export interface TerminalCommand {
  name: string;
  description: string;
  output: string[];
  delay?: number;
}

const agentList = [
  { name: 'agente-principal', role: 'Lógica, estructura, integraciones', status: 'active' },
  { name: 'agente-design', role: 'CSS, responsive, animaciones', status: 'active' },
  { name: 'agente-web-3d', role: 'Three.js, R3F, Spline, shaders', status: 'active' },
  { name: 'agente-web-motion', role: 'GSAP, ScrollTrigger, Lenis', status: 'active' },
  { name: 'agente-web-copy', role: 'Copy, CTAs, storytelling', status: 'active' },
  { name: 'agente-web-qa', role: 'Lighthouse, anti-slop, a11y', status: 'active' },
  { name: 'agente-marketing-strategist', role: 'Estrategia, GTM, posicionamiento', status: 'standby' },
  { name: 'agente-growth-seo-geo', role: 'SEO/GEO growth, keywords', status: 'standby' },
  { name: 'agente-security-auditor', role: 'Secretos, permisos, supply-chain', status: 'standby' },
  { name: 'agente-obsidian-brain', role: 'Obsidian vault, notas, MOCs', status: 'standby' },
];

const workflowList = [
  { name: 'web-factory', desc: 'Orquestación tipo Lovable con 5 agentes sandboxed' },
  { name: 'world-class-web', desc: 'Pipeline 10 etapas para web 3D inmersiva' },
  { name: 'spec_kit', desc: 'Spec-driven development' },
  { name: 'parallel_agents', desc: 'Tareas independientes en paralelo' },
  { name: 'validation', desc: 'Quality gate antes de declarar listo' },
  { name: 'feedback_loop', desc: 'Aprendizaje de errores en tiempo real' },
  { name: 'multiagent_review_loop', desc: 'Crear → criticar → red team → plan' },
  { name: 'venture_loop', desc: 'Loop idea→MVP→landing→distribución→medición' },
];

const skillList = [
  'premium-web-stack', 'brainstorming', 'systematic-debugging',
  'test-driven-development', 'writing-plans', 'dispatching-parallel-agents',
  'verification-before-completion', 'requesting-code-review',
  'css-animations', 'frontend-design', 'seo-geo-growth',
  'product-foundry', 'ai-production-architecture',
];

export const commands: Record<string, TerminalCommand> = {
  help: {
    name: 'help',
    description: 'Show available commands',
    output: [
      '╔══════════════════════════════════════════════════╗',
      '║         NEURAL COMMAND CENTER v2.0               ║',
      '╠══════════════════════════════════════════════════╣',
      '║  help          Show this help message             ║',
      '║  ls agents     List all active agents             ║',
      '║  ls workflows  List available workflows          ║',
      '║  ls skills     List available skills             ║',
      '║  show <name>   Show details of agent/workflow     ║',
      '║  stats         Show system statistics            ║',
      '║  run <wf>      Simulate running a workflow       ║',
      '║  whoami        About Nacho Palmeri               ║',
      '║  contact       Get contact info                  ║',
      '║  clear         Clear terminal                    ║',
      '╚══════════════════════════════════════════════════╝',
    ],
  },
  'ls agents': {
    name: 'ls agents',
    description: 'List all active agents',
    output: [
      '┌─────────────────────────┬──────────────────────────────┬──────────┐',
      '│ Agent                   │ Role                         │ Status   │',
      '├─────────────────────────┼──────────────────────────────┼──────────┤',
      ...agentList.map(a => `│ ${a.name.padEnd(23)} │ ${a.role.padEnd(28)} │ ${a.status.padEnd(8)} │`),
      '└─────────────────────────┴──────────────────────────────┴──────────┘',
      '',
      `Total: ${agentList.length} agents (${agentList.filter(a => a.status === 'active').length} active, ${agentList.filter(a => a.status === 'standby').length} standby)`,
    ],
  },
  'ls workflows': {
    name: 'ls workflows',
    description: 'List available workflows',
    output: [
      '┌───────────────────────────┬──────────────────────────────────────────┐',
      '│ Workflow                  │ Description                              │',
      '├───────────────────────────┼──────────────────────────────────────────┤',
      ...workflowList.map(w => `│ ${w.name.padEnd(25)} │ ${w.desc.padEnd(40)} │`),
      '└───────────────────────────┴──────────────────────────────────────────┘',
      '',
      `Total: ${workflowList.length} workflows loaded`,
    ],
  },
  'ls skills': {
    name: 'ls skills',
    description: 'List available skills',
    output: [
      'Available skills:',
      '',
      ...skillList.map((s, i) => `  ${i + 1}. ${s}`),
      '',
      `Total: ${skillList.length} skills loaded`,
    ],
  },
  stats: {
    name: 'stats',
    description: 'Show system statistics',
    output: [
      '  ╭─────────────────────────────────╮',
      '  │     SYSTEM STATISTICS           │',
      '  ├─────────────────────────────────┤',
      '  │  Workflows:    44               │',
      '  │  Agents:       17               │',
      '  │  Skills:       78               │',
      '  │  Tests:        141              │',
      '  │  Uptime:       99.9%            │',
      '  │  Latency:      42ms avg         │',
      '  │  Last deploy:  2 hours ago      │',
      '  ╰─────────────────────────────────╯',
    ],
  },
  whoami: {
    name: 'whoami',
    description: 'About Nacho Palmeri',
    output: [
      '  ┌──────────────────────────────────────┐',
      '  │  NACHO PALMERI                       │',
      '  │  Builder · AI Systems · Automation   │',
      '  ├──────────────────────────────────────┤',
      '  │  Building agent systems that ship.   │',
      '  │  44 workflows, 17 agents, 78 skills. │',
      '  │  Python + Next.js + Claude API.       │',
      '  │                                      │',
      '  │  "Ship while you sleep."             │',
      '  └──────────────────────────────────────┘',
    ],
  },
  contact: {
    name: 'contact',
    description: 'Get contact info',
    output: [
      '  📧 Email:    nacho@pisculabs.com',
      '  💼 LinkedIn: linkedin.com/in/nachopalmeri',
      '  🐙 GitHub:   github.com/nachopalmeri',
      '  🌐 Web:      nachopalmeri.dev',
    ],
  },
  'run web-factory': {
    name: 'run web-factory',
    description: 'Simulate running web-factory workflow',
    delay: 100,
    output: [
      '▶ Initializing web-factory workflow...',
      '  ▸ Phase 1: Plan Mode — Briefing complete ✓',
      '  ▸ Phase 1: Concept visual defined ✓',
      '  ▸ Phase 1: Agent assignment complete ✓',
      '  ▸ Phase 2: Spawning 5 sandboxed agents...',
      '    → agente-web-layout: ACTIVE',
      '    → agente-web-3d: ACTIVE',
      '    → agente-web-motion: ACTIVE',
      '    → agente-web-copy: ACTIVE',
      '    → agente-web-qa: STANDBY',
      '  ▸ Phase 2: Building in parallel...',
      '  ▸ Phase 2: Integration complete ✓',
      '  ▸ Phase 3: Polish Mode — Anti-slop pass',
      '  ▸ Phase 3: Lighthouse audit: 96/100 ✓',
      '▶ web-factory complete. Build ready for deploy.',
    ],
  },
  'run spec_kit': {
    name: 'run spec_kit',
    description: 'Simulate running spec_kit workflow',
    delay: 100,
    output: [
      '▶ Initializing spec_kit workflow...',
      '  ▸ Loading constitution...',
      '  ▸ Generating spec from requirements ✓',
      '  ▸ Creating implementation plan ✓',
      '  ▸ Breaking down into tasks ✓',
      '  ▸ Ready for implementation.',
      '▶ spec_kit complete. 12 tasks generated.',
    ],
  },
  'run validation': {
    name: 'run validation',
    description: 'Simulate running validation workflow',
    delay: 80,
    output: [
      '▶ Running validation...',
      '  ▸ Type check: PASS ✓',
      '  ▸ Lint: PASS ✓',
      '  ▸ Build: PASS ✓',
      '  ▸ Lighthouse: 96/100 ✓',
      '  ▸ Anti-slop: 9/9 checks PASS ✓',
      '▶ Validation complete. Ready to ship.',
    ],
  },
};

export function processCommand(input: string): TerminalCommand | null {
  const trimmed = input.trim().toLowerCase();

  if (trimmed === 'clear') return null;
  if (trimmed === '') return null;

  if (commands[trimmed]) return commands[trimmed];

  if (trimmed.startsWith('show ')) {
    const name = trimmed.replace('show ', '');
    const agent = agentList.find(a => a.name === name);
    if (agent) {
      return {
        name: `show ${name}`,
        description: `Show details for ${name}`,
        output: [
          `  Agent: ${agent.name}`,
          `  Role:  ${agent.role}`,
          `  Status: ${agent.status}`,
          `  Workflows: ${Math.floor(Math.random() * 10) + 1} assigned`,
          `  Skills: ${Math.floor(Math.random() * 15) + 5} loaded`,
          `  Last run: ${Math.floor(Math.random() * 24)} hours ago`,
        ],
      };
    }
    const workflow = workflowList.find(w => w.name === name);
    if (workflow) {
      return {
        name: `show ${name}`,
        description: `Show details for ${name}`,
        output: [
          `  Workflow: ${workflow.name}`,
          `  Description: ${workflow.desc}`,
          `  Agents required: ${Math.floor(Math.random() * 4) + 1}`,
          `  Avg runtime: ${Math.floor(Math.random() * 30) + 5}s`,
        ],
      };
    }
  }

  if (trimmed.startsWith('run ')) {
    const wfName = trimmed.replace('run ', '');
    const wf = workflowList.find(w => w.name === wfName);
    if (wf) {
      return {
        name: `run ${wfName}`,
        description: `Simulate running ${wfName}`,
        delay: 80,
        output: [
          `▶ Initializing ${wfName}...`,
          `  ▸ ${wf.desc}`,
          `  ▸ Spawning agents...`,
          `  ▸ Processing...`,
          `▶ ${wfName} complete.`,
        ],
      };
    }
  }

  return {
    name: trimmed,
    description: 'Unknown command',
    output: [`  Command not found: ${trimmed}`, '  Type "help" for available commands.'],
  };
}
