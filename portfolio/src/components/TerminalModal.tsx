'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Terminal } from 'lucide-react';
import { processCommand } from '@/lib/terminal-commands';

interface TerminalLine {
  type: 'input' | 'output';
  content: string;
  delay?: number;
}

export default function TerminalModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
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

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div
        className="w-full max-w-3xl bg-[#0d1117] rounded-xl border border-cyan/30 shadow-2xl shadow-cyan/10 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title Bar */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-[#161b22] border-b border-cyan/20">
          <div className="flex items-center gap-2">
            <Terminal size={16} className="text-cyan" />
            <span className="text-sm font-mono text-cyan">neural-command-center</span>
            <span className="text-xs font-mono text-gray-500 ml-2">— bash</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <div className="w-3 h-3 rounded-full bg-green-500/60" />
            <button
              onClick={onClose}
              className="w-3 h-3 rounded-full bg-red-500/80 hover:bg-red-500 transition-colors"
            />
          </div>
        </div>

        {/* Terminal Content */}
        <div
          ref={terminalRef}
          className="h-[500px] overflow-y-auto p-4 font-mono text-sm leading-relaxed custom-scrollbar"
          onClick={() => inputRef.current?.focus()}
        >
          {lines.map((line, i) => (
            <div key={i} className={`${line.type === 'input' ? 'text-cyan' : 'text-gray-300'} whitespace-pre`}>
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
            />
            {isProcessing && <span className="animate-pulse text-cyan">▊</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
