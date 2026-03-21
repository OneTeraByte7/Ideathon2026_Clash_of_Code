import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function StatsBar({ patients = [], alerts = [] }) {
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

  const total = patients.length;
  const critical = patients.filter((p) => p.risk_level === "critical").length;
  const warning = patients.filter((p) => p.risk_level === "warning").length;
  const stable = patients.filter((p) => p.risk_level === "normal").length;
  const activeAlerts = alerts.filter((a) => !a.resolved).length;

  const stats = [
    { label: "TOTAL PATIENTS", value: total,       color: isDark ? "rgba(255,255,255,0.5)" : "rgba(0,0,0,0.5)", glow: false },
    { label: "CRITICAL",        value: critical,    color: "#ff2d78", glow: true },
    { label: "WARNING",         value: warning,     color: "#f59e0b", glow: false },
    { label: "STABLE",          value: stable,      color: "#00f5d4", glow: false },
    { label: "ACTIVE ALERTS",   value: activeAlerts,color: "#ff2d78", glow: critical > 0 },
  ];

  return (
    <div className="grid grid-cols-5 gap-4 mb-8">
      {stats.map((s, i) => (
        <motion.div
          key={s.label}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05, duration: 0.4 }}
          className="rounded-xl px-5 py-4 flex flex-col gap-1 hover:shadow-md transition-all"
          style={{
            background: isDark ? "#0d1220" : "#ffffff",
            border: `1px solid ${s.glow && s.value > 0 ? s.color + "44" : isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.08)"}`,
            boxShadow: s.glow && s.value > 0 ? `0 0 20px ${s.color}22` : "none",
          }}
        >
          <span className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-40 text-white' : 'opacity-50 text-gray-900'} font-semibold`}>{s.label}</span>
          <motion.span
            key={s.value}
            initial={{ scale: 1.3, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="font-display font-bold text-3xl leading-none"
            style={{ color: s.value > 0 ? s.color : isDark ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.15)", textShadow: s.glow && s.value > 0 ? `0 0 20px ${s.color}` : "none" }}
          >
            {s.value.toString().padStart(2, "0")}
          </motion.span>
        </motion.div>
      ))}
    </div>
  );
}
