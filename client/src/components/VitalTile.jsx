import { motion } from "framer-motion";
import React from "react";

const METRICS = {
  heart_rate:       { label: "Heart Rate",   unit: "bpm",       normal: [60, 90],   icon: "♥" },
  systolic_bp:      { label: "Systolic BP",  unit: "mmHg",      normal: [100, 140], icon: "⊕" },
  respiratory_rate: { label: "Resp Rate",    unit: "br/min",    normal: [12, 20],   icon: "≋" },
  temperature:      { label: "Temperature",  unit: "°C",        normal: [36, 38],   icon: "◈" },
  spo2:             { label: "SpO₂",         unit: "%",         normal: [95, 100],  icon: "◉" },
  lactate:          { label: "Lactate",      unit: "mmol/L",    normal: [0.5, 2.0], icon: "⬡" },
};

function getStatus(key, value) {
  const m = METRICS[key];
  if (!m || value == null) return "normal";
  const [lo, hi] = m.normal;
  if (key === "heart_rate") {
    if (value >= 110) return "critical";
    if (value >= 95 || value < 55) return "warning";
  }
  if (key === "systolic_bp") {
    if (value <= 90) return "critical";
    if (value <= 105) return "warning";
  }
  if (key === "respiratory_rate") {
    if (value >= 26) return "critical";
    if (value >= 22) return "warning";
  }
  if (key === "spo2") {
    if (value <= 88) return "critical";
    if (value <= 92) return "warning";
  }
  if (key === "lactate") {
    if (value >= 4) return "critical";
    if (value >= 2.2) return "warning";
  }
  if (key === "temperature") {
    if (value >= 39.5 || value < 35) return "critical";
    if (value >= 38.3 || value < 36) return "warning";
  }
  return "normal";
}

const STATUS_STYLES = {
  normal:   { 
    color: "#00f5d4", 
    colorLight: "#06b6d4",
    bg: "rgba(0,245,212,0.05)",
    bgLight: "rgba(6,182,212,0.08)",
    border: "rgba(0,245,212,0.15)",
    borderLight: "rgba(6,182,212,0.25)"
  },
  warning:  { 
    color: "#f59e0b", 
    colorLight: "#eab308",
    bg: "rgba(245,158,11,0.07)",
    bgLight: "rgba(234,179,8,0.1)",
    border: "rgba(245,158,11,0.3)",
    borderLight: "rgba(234,179,8,0.35)"
  },
  critical: { 
    color: "#ff2d78", 
    colorLight: "#ec4899",
    bg: "rgba(255,45,120,0.07)",
    bgLight: "rgba(236,72,153,0.1)",
    border: "rgba(255,45,120,0.35)",
    borderLight: "rgba(236,72,153,0.4)"
  },
};

export default function VitalTile({ metricKey, value, index = 0 }) {
  const [isDark, setIsDark] = React.useState(true);
  
  React.useEffect(() => {
    const checkTheme = () => {
      setIsDark(document.body.classList.contains('light') === false);
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const meta = METRICS[metricKey];
  if (!meta) return null;
  const status = getStatus(metricKey, value);
  const s = STATUS_STYLES[status];
  const isCritical = status === "critical";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4 }}
      className="relative rounded-xl p-3 flex flex-col gap-1 overflow-hidden"
      style={{
        background: isDark ? s.bg : s.bgLight,
        border: `1px solid ${isDark ? s.border : s.borderLight}`,
        animation: isCritical ? "criticalBorder 1.5s ease-in-out infinite" : undefined,
      }}
    >
      {/* Icon top-right */}
      <div
        className="absolute top-2 right-3 font-mono text-lg opacity-30"
        style={{ color: isDark ? s.color : s.colorLight }}
      >
        {meta.icon}
      </div>

      <span className={`font-mono text-xs tracking-widest uppercase opacity-40 ${isDark ? 'text-white' : 'text-gray-700'}`}>
        {meta.label}
      </span>

      <div className="flex items-baseline gap-1">
        <motion.span
          key={value}
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-display font-bold text-2xl leading-none"
          style={{ color: isDark ? s.color : s.colorLight, textShadow: `0 0 16px ${isDark ? s.color : s.colorLight}44` }}
        >
          {value != null ? (typeof value === "number" ? value.toFixed(value % 1 === 0 ? 0 : 1) : value) : "—"}
        </motion.span>
        <span className={`font-mono text-xs opacity-40 ${isDark ? 'text-white' : 'text-gray-700'}`}>{meta.unit}</span>
      </div>

      {/* Status bar at bottom */}
      <div className="h-0.5 rounded-full mt-1" style={{ background: isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.1)" }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: isDark ? s.color : s.colorLight, boxShadow: `0 0 6px ${isDark ? s.color : s.colorLight}` }}
          initial={{ width: 0 }}
          animate={{ width: status === "critical" ? "100%" : status === "warning" ? "65%" : "30%" }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  );
}
