import { useEffect, useRef } from "react";

const ECG_PATH = "M0,50 L20,50 L25,50 L30,10 L35,90 L40,50 L50,50 L55,50 L60,20 L65,80 L70,50 L100,50";

export default function ECGLine({ color = "#00f5d4", height = 60, className = "" }) {
  const pathRef = useRef(null);

  useEffect(() => {
    if (!pathRef.current) return;
    const len = pathRef.current.getTotalLength?.() || 300;
    pathRef.current.style.strokeDasharray = len;
    pathRef.current.style.strokeDashoffset = len;

    let start = null;
    const duration = 2200;

    const step = (ts) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      if (pathRef.current) {
        pathRef.current.style.strokeDashoffset = len * (1 - progress);
      }
      if (progress < 1) requestAnimationFrame(step);
      else {
        start = null;
        setTimeout(() => requestAnimationFrame(step), 400);
      }
    };
    requestAnimationFrame(step);
  }, []);

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className={`w-full ${className}`} style={{ height }}>
      <defs>
        <filter id="ecgGlow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
      <path
        ref={pathRef}
        d={ECG_PATH}
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        filter="url(#ecgGlow)"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
}
