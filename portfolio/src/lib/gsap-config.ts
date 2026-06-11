'use client';

import { useEffect } from 'react';

export function useGSAPScroll() {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    // Default settings
    ScrollTrigger.defaults({
      toggleActions: 'play none none reverse',
      start: 'top 85%',
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger: any) => trigger.kill());
    };
  }, []);
}

export function useParallax(selector: string, speed: number = 0.5) {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    const elements = document.querySelectorAll(selector);
    elements.forEach((el) => {
      gsap.to(el, {
        y: () => speed * 100,
        ease: 'none',
        scrollTrigger: {
          trigger: el,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true,
        },
      });
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger: any) => trigger.kill());
    };
  }, [selector, speed]);
}

export function usePinnedSection(selector: string) {
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const gsap = require('gsap').default;
    const ScrollTrigger = require('gsap/ScrollTrigger').default;
    gsap.registerPlugin(ScrollTrigger);

    const elements = document.querySelectorAll(selector);
    elements.forEach((el) => {
      gsap.to(el, {
        scrollTrigger: {
          trigger: el,
          start: 'top top',
          end: '+=100%',
          pin: true,
          pinSpacing: true,
        },
      });
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger: any) => trigger.kill());
    };
  }, [selector]);
}
