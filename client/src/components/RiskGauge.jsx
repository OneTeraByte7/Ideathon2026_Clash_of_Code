import { motion } from "framer-motion";
import { useState, useEffect } from "react";

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getColor(score) {
  if (score >= 70) return "#ff2d78";
  if (score >= 40) return "#f59e0b";
  return "#00f5d4";
}

function getLabel(score) {
  if (score >= 70) return "CRITICAL";
  if (score >= 40) return "WARNING";
  return "STABLE";
}

export default function RiskGauge({ score = 0, size = 140 }) {
  const [isDark, setIsDark] = useState(true);
  
  useEffect(() => {
    const checkTheme = () => {
      setIsDark(document.body.classList.contains('light') === false);
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const color = getColor(score);
  const label = getLabel(score);
  const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
  const isCritical = score >= 70;
  const trackColor = isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.1)";
  const labelColor = isDark ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.5)";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Outer ring pulse for critical */}
      {isCritical && (
        <div
          className="absolute rounded-full border-2 border-pulse animate-ping-slow"
          style={{ width: size + 16, height: size + 16, animationDuration: "1.5s" }}
        />
      )}

      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        {/* Track */}
        <circle
          cx={size / 2} cy={size / 2} r={RADIUS}
          fill="none" stroke={trackColor}
          strokeWidth="8"
        />
        {/* Progress */}
        <motion.circle
          cx={size / 2} cy={size / 2} r={RADIUS}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          initial={{ strokeDashoffset: CIRCUMFERENCE }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          style={{ filter: `drop-shadow(0 0 8px ${color})` }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute flex flex-col items-center">
        <motion.span
          className="font-display font-bold leading-none"
          style={{ fontSize: size * 0.22, color }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          {Math.round(score)}
        </motion.span>
        <span
          className="font-mono tracking-widest uppercase"
          style={{ fontSize: size * 0.095, color: labelColor, marginTop: 2 }}
        >
          {label}
        </span>
      </div>
    </div>
  );
}
