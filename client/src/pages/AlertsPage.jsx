import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getAlerts, resolveAlert } from "../lib/api";

const LEVEL_META = {
  critical: { color: "#ff2d78", bg: "rgba(255,45,120,0.07)", border: "rgba(255,45,120,0.25)", icon: "☠" },
  warning:  { color: "#f59e0b", bg: "rgba(245,158,11,0.07)", border: "rgba(245,158,11,0.25)", icon: "⚠" },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [resolving, setResolving] = useState(null);
  const [tab, setTab] = useState("active");
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

  const load = () => getAlerts(tab === "resolved").then(setAlerts).catch(() => {
    // Silently ignore load errors
  });

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, [tab]);

  const handleResolve = async (id) => {
    setResolving(id);
    try { await resolveAlert(id); await load(); }
    finally { setResolving(null); }
  };

  const critical = alerts.filter(a => a.level === "critical");
  const warning = alerts.filter(a => a.level === "warning");

  return (
    <div className="min-h-screen grid-bg" style={{ paddingTop: "72px" }}>
      <div className="max-w-5xl mx-auto px-8 py-10">

        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className={`font-display font-bold text-4xl ${isDark ? 'text-white' : 'text-gray-900'} mb-2`}>Alert Center</h1>
          <p className={`font-mono text-xs ${isDark ? 'opacity-40' : 'opacity-60'} tracking-wide`}>SEPSIS SIGNAL MONITORING · AUTO-ESCALATION ACTIVE</p>
        </motion.div>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-5 mb-10">
          {[
            { label: "CRITICAL ACTIVE", value: critical.length, color: "#ff2d78", icon: "☠" },
            { label: "WARNINGS ACTIVE", value: warning.length, color: "#f59e0b", icon: "⚠" },
            { label: "TOTAL EVENTS",    value: alerts.length,   color: "#00f5d4", icon: "◈" },
          ].map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl p-6 hover:shadow-lg transition-all"
              style={{ 
                background: isDark ? "#0d1220" : "#ffffff",
                border: `1px solid ${s.color}22`, 
                boxShadow: s.value > 0 ? `0 0 30px ${s.color}10` : "none" 
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-40' : 'opacity-60'}`}>{s.label}</span>
                <span className="text-2xl" style={{ color: s.color, opacity: 0.6 }}>{s.icon}</span>
              </div>
              <span className="font-display font-bold text-4xl" style={{ color: s.color, textShadow: s.value > 0 ? `0 0 30px ${s.color}` : "none" }}>
                {s.value.toString().padStart(2, "0")}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Tab switch */}
        <div className="flex gap-3 mb-6">
          {["active", "resolved"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="px-5 py-2 rounded-lg font-mono text-xs tracking-widest uppercase transition-all hover:shadow-md"
              style={{
                background: tab === t ? "rgba(0,245,212,0.12)" : "rgba(255,255,255,0.03)",
                border: `1px solid ${tab === t ? "rgba(0,245,212,0.4)" : "rgba(255,255,255,0.08)"}`,
                color: tab === t ? "#00f5d4" : "rgba(255,255,255,0.4)",
              }}
            >
              {t === "active" ? "Active Alerts" : "Resolved"}
            </button>
          ))}
        </div>

        {/* Alert list */}
        <div className="flex flex-col gap-4">
          <AnimatePresence mode="popLayout">
            {alerts.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-20 rounded-2xl"
                style={{ border: "1px dashed rgba(255,255,255,0.08)", background: "rgba(13,18,32,0.3)" }}
              >
                <div className="text-4xl mb-3 opacity-15">✓</div>
                <p className="font-mono text-xs opacity-30 tracking-widest mb-1">{tab === "active" ? "ALL CLEAR — NO ACTIVE ALERTS" : "NO RESOLVED ALERTS"}</p>
                <p className="font-mono text-xs opacity-15">System operating normally</p>
              </motion.div>
            ) : (
              alerts.map((a, i) => {
                const m = LEVEL_META[a.level] || LEVEL_META.warning;
                return (
                  <motion.div
                    key={a.id}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20, height: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="rounded-xl p-5 flex items-start gap-4 hover:shadow-lg transition-all"
                    style={{ background: m.bg, border: `1px solid ${m.border}` }}
                  >
                    {/* Level badge */}
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0 mt-0.5"
                      style={{ background: `${m.color}18`, border: `1px solid ${m.color}30`, color: m.color }}
                    >
                      {m.icon}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-display font-bold text-sm" style={{ color: m.color }}>
                          {a.level.toUpperCase()}
                        </span>
                        <span className="font-mono text-xs opacity-40">PATIENT #{a.patient_id}</span>
                        <span className="font-mono text-xs opacity-40 ml-auto">
                          {new Date(a.triggered_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="font-mono text-xs text-white opacity-60 leading-relaxed mb-3">{a.message}</p>
                      <div className="flex gap-4 text-xs">
                        <span className="font-mono opacity-30">
                          Nurse: <span style={{ color: a.nurse_notified ? "#39ff14" : "#ff2d78" }}>{a.nurse_notified ? "✓ notified" : "✗ pending"}</span>
                        </span>
                        <span className="font-mono opacity-30">
                          Doctor: <span style={{ color: a.doctor_notified ? "#39ff14" : a.level === "warning" ? "#999" : "#ff2d78" }}>{a.doctor_notified ? "✓ notified" : a.level === "warning" ? "—" : "✗ pending"}</span>
                        </span>
                      </div>
                    </div>

                    {tab === "active" && (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleResolve(a.id)}
                        disabled={resolving === a.id}
                        className="flex-shrink-0 px-4 py-2 rounded-lg font-mono text-xs tracking-widest transition-all hover:shadow-md"
                        style={{
                          background: "rgba(0,245,212,0.12)",
                          border: "1px solid rgba(0,245,212,0.3)",
                          color: "#00f5d4",
                          opacity: resolving === a.id ? 0.5 : 1,
                        }}
                      >
                        {resolving === a.id ? "..." : "RESOLVE"}
                      </motion.button>
                    )}
                  </motion.div>
                );
              })
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
