'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal } from 'lucide-react';
import { processCommand } from '@/lib/terminal-commands';

interface TerminalLine {
  type: 'input' | 'output';
  content: string;
}

export default function TerminalSection() {
  const [lines, setLines] = useState<TerminalLine[]>([
    { type: 'output', content: '╔══════════════════════════════════════════════════╗' },
    { type: 'output', content: '║     NEURAL COMMAND CENTER v2.0 — Nacho Palmeri  ║' },
    { type: 'output', content: '║     44 workflows · 17 agents · 78 skills        ║' },
    { type: 'output', content: '╚══════════════════════════════════════════════════╝' },
    { type: 'output', content: '' },
    { type: 'output', content: '  Type "help" for available commands.' },
    { type: 'output', content: '' },
  ]);
  const [currentInput, setCurrentInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  const handleCommand = useCallback(async (input: string) => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setLines(prev => [...prev, { type: 'input', content: `❯ ${trimmed}` }]);

    if (trimmed.toLowerCase() === 'clear') {
      setLines([]);
      setCurrentInput('');
      return;
    }

    setIsProcessing(true);
    const command = processCommand(trimmed);

    if (command) {
      for (const line of command.output) {
        await new Promise(r => setTimeout(r, command.delay || 30));
        setLines(prev => [...prev, { type: 'output', content: line }]);
      }
    }

    setLines(prev => [...prev, { type: 'output', content: '' }]);
    setIsProcessing(false);
    setCurrentInput('');
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isProcessing) {
      handleCommand(currentInput);
    }
  };

  return (
    <section id="terminal" className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-6">Terminal</h2>

        <div className="bg-[#0d1117] rounded-xl border border-white/10 overflow-hidden">
          {/* Title Bar */}
          <div className="flex items-center gap-2 px-4 py-2.5 bg-[#161b22] border-b border-white/10">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <div className="w-3 h-3 rounded-full bg-green-500/60" />
            <Terminal size={14} className="text-cyan ml-2" />
            <span className="text-xs font-mono text-gray-500">neural-command-center — bash</span>
          </div>

          {/* Terminal Content */}
          <div
            ref={terminalRef}
            className="h-[340px] overflow-y-auto p-4 font-mono text-sm leading-relaxed"
            onClick={() => inputRef.current?.focus()}
          >
            {lines.map((line, i) => (
              <div key={i} className={`${line.type === 'input' ? 'text-cyan' : 'text-gray-400'} whitespace-pre`}>
                {line.content}
              </div>
            ))}

            {/* Input Line */}
            <div className="flex items-center gap-2 text-cyan">
              <span>❯</span>
              <input
                ref={inputRef}
                type="text"
                value={currentInput}
                onChange={(e) => setCurrentInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isProcessing}
                className="flex-1 bg-transparent outline-none text-gray-100 font-mono text-sm caret-cyan"
                autoFocus
                spellCheck={false}
                autoComplete="off"
                placeholder="Type a command..."
              />
              {isProcessing && <span className="animate-pulse text-cyan">▊</span>}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
