'use client';

import { useEffect, useRef, useState } from 'react';
import { Github } from 'lucide-react';

interface ContributionDay {
  date: string;
  contributionCount: number;
  color: string;
}

interface Week {
  contributionDays: ContributionDay[];
}

interface GithubData {
  totalContributions: number;
  weeks: Week[];
}

const levelColors = [
  'bg-white/5',     // 0
  'bg-cyan/20',     // 1
  'bg-cyan/40',     // 2
  'bg-cyan/60',     // 3
  'bg-cyan/80',     // 4
];

function getLevel(count: number): number {
  if (count === 0) return 0;
  if (count <= 2) return 1;
  if (count <= 5) return 2;
  if (count <= 9) return 3;
  return 4;
}

export default function GitHubActivity() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<GithubData | null>(null);
  const [hoveredDay, setHoveredDay] = useState<ContributionDay | null>(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    fetch('/api/github')
      .then(res => res.json())
      .then(setData)
      .catch(() => setData(null));
  }, []);

  // Show last 26 weeks
  const weeks = data?.weeks?.slice(-26) || [];

  return (
    <section ref={sectionRef} className="py-16 px-6 md:px-8 border-t border-white/5">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Github size={16} className="text-gray-500" />
          <h2 className="text-xs uppercase tracking-widest text-gray-500">GitHub Activity</h2>
          <a
            href="https://github.com/nachopalmeri"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-600 hover:text-cyan font-mono transition-colors ml-auto"
          >
            @nachopalmeri →
          </a>
        </div>

        {data ? (
          <>
            <p className="text-sm text-gray-500 font-mono mb-6">
              {data.totalContributions} contribuciones en {new Date().getFullYear()}
            </p>

            <div className="overflow-x-auto pb-2">
              <div className="flex gap-[3px]" style={{ minWidth: weeks.length * 15 }}>
                {weeks.map((week, weekIdx) => (
                  <div key={weekIdx} className="flex flex-col gap-[3px]">
                    {week.contributionDays.map((day) => {
                      const level = getLevel(day.contributionCount);
                      return (
                        <div
                          key={day.date}
                          className={`w-[12px] h-[12px] rounded-sm ${levelColors[level]} hover:ring-1 hover:ring-cyan/50 transition-all cursor-pointer`}
                          onMouseEnter={(e) => {
                            setHoveredDay(day);
                            setHoverPos({ x: e.clientX, y: e.clientY });
                          }}
                          onMouseLeave={() => setHoveredDay(null)}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>

            {/* Legend */}
            <div className="flex items-center gap-2 mt-4 text-[10px] text-gray-600 font-mono">
              <span>Menos</span>
              {levelColors.map((cls, i) => (
                <div key={i} className={`w-[12px] h-[12px] rounded-sm ${cls}`} />
              ))}
              <span>Más</span>
            </div>
          </>
        ) : (
          <div className="p-6 rounded-lg border border-white/5 bg-white/[0.02] text-center">
            <p className="text-sm text-gray-500 font-mono">
              GitHub activity requires a GITHUB_TOKEN in .env.local
            </p>
            <a
              href="https://github.com/nachopalmeri"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-cyan hover:underline font-mono mt-2 inline-block"
            >
              Ver perfil en GitHub →
            </a>
          </div>
        )}

        {/* Tooltip */}
        {hoveredDay && data && (
          <div
            className="fixed z-50 bg-[#0d1117] border border-cyan/20 rounded-md px-3 py-2 text-xs font-mono shadow-lg pointer-events-none"
            style={{ left: hoverPos.x + 12, top: hoverPos.y - 40 }}
          >
            <div className="text-gray-300">
              {hoveredDay.contributionCount} contribuciones
            </div>
            <div className="text-gray-600">{hoveredDay.date}</div>
          </div>
        )}
      </div>
    </section>
  );
}
