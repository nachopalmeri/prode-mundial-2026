'use client';

import { useEffect, useRef } from 'react';

export default function CustomCursor() {
  const ringRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);
  const is3DRef = useRef(false);
  const posRef = useRef({ x: 0, y: 0 });
  const rafRef = useRef<number>(0);

  useEffect(() => {
    if (typeof window === 'undefined' || window.matchMedia('(pointer: coarse)').matches) return;

    const ring = ringRef.current;
    const dot = dotRef.current;
    if (!ring || !dot) return;

    let visible = false;

    const show = () => {
      if (!visible) {
        visible = true;
        ring.style.opacity = '1';
        dot.style.opacity = '1';
      }
    };

    const hide = () => {
      visible = false;
      ring.style.opacity = '0';
      dot.style.opacity = '0';
    };

    const handleMove = (e: MouseEvent) => {
      posRef.current = { x: e.clientX, y: e.clientY };
      show();

      const target = e.target as HTMLElement;
      const is3D = target.closest('[data-3d-cursor]') !== null;
      if (is3DRef.current !== is3D) {
        is3DRef.current = is3D;
        ring.style.borderColor = is3D ? '#00d9ff' : 'rgba(255,255,255,0.2)';
        ring.style.transform = is3D ? 'scale(1.5)' : 'scale(1)';
        dot.style.background = is3D ? '#00d9ff' : 'rgba(255,255,255,0.5)';
      }
    };

    const animate = () => {
      const { x, y } = posRef.current;
      dot.style.left = `${x - 3}px`;
      dot.style.top = `${y - 3}px`;
      ring.style.left = `${x - 20}px`;
      ring.style.top = `${y - 20}px`;
      rafRef.current = requestAnimationFrame(animate);
    };

    document.addEventListener('mousemove', handleMove, { passive: true });
    document.addEventListener('mouseleave', hide);
    document.addEventListener('mouseenter', show);
    rafRef.current = requestAnimationFrame(animate);

    return () => {
      document.removeEventListener('mousemove', handleMove);
      document.removeEventListener('mouseleave', hide);
      document.removeEventListener('mouseenter', show);
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <>
      <div
        ref={ringRef}
        style={{
          position: 'fixed',
          width: 40,
          height: 40,
          borderRadius: '50%',
          border: '1.5px solid rgba(255,255,255,0.2)',
          pointerEvents: 'none',
          zIndex: 9999,
          opacity: 0,
          transition: 'transform 0.2s ease-out, border-color 0.2s ease-out',
          mixBlendMode: 'difference',
        }}
      />
      <div
        ref={dotRef}
        style={{
          position: 'fixed',
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.5)',
          pointerEvents: 'none',
          zIndex: 9999,
          opacity: 0,
          transition: 'background 0.2s ease-out',
        }}
      />
    </>
  );
}
