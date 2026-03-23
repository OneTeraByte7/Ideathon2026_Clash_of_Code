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

  const load = () => getAlerts(tab === "resolved").then(setAlerts).catch(() => {});

  useEffect(() => { 
    load(); 
    const t = setInterval(load, 5000); 
    return () => clearInterval(t); 
  }, [tab]);

  const handleResolve = async (id) => {
    setResolving(id);
    try { 
      await resolveAlert(id); 
      await load(); 
    }
    finally { 
      setResolving(null); 
    }
  };

  const critical = alerts.filter(a => a.level === "critical");
  const warning = alerts.filter(a => a.level === "warning");

  return (
    <div className="min-h-screen grid-bg" style={{ paddingTop: "72px" }}>
      <div className="max-w-5xl mx-auto px-6 py-8">

        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="font-display font-bold text-3xl text-white">Alert Center</h1>
          <p className="font-mono text-xs opacity-30 mt-1 tracking-widest">SEPSIS SIGNAL MONITORING · AUTO-ESCALATION ACTIVE</p>
        </motion.div>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
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
              className="rounded-2xl p-5"
              style={{ background: "#0d1220", border: `1px solid ${s.color}22`, boxShadow: s.value > 0 ? `0 0 30px ${s.color}10` : "none" }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs tracking-widest opacity-30">{s.label}</span>
                <span className="text-xl" style={{ color: s.color, opacity: 0.5 }}>{s.icon}</span>
              </div>
              <span className="font-display font-bold text-4xl" style={{ color: s.color, textShadow: s.value > 0 ? `0 0 30px ${s.color}` : "none" }}>
                {s.value.toString().padStart(2, "0")}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Tab switch */}
        <div className="flex gap-2 mb-5">
          {["active", "resolved"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="px-4 py-2 rounded-lg font-mono text-xs tracking-widest uppercase transition-all"
              style={{
                background: tab === t ? "rgba(0,245,212,0.1)" : "rgba(255,255,255,0.03)",
                border: `1px solid ${tab === t ? "rgba(0,245,212,0.3)" : "rgba(255,255,255,0.06)"}`,
                color: tab === t ? "#00f5d4" : "rgba(255,255,255,0.3)",
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Alert list */}
        <div className="flex flex-col gap-3">
          <AnimatePresence mode="popLayout">
            {alerts.length === 0 ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-20 font-mono text-xs opacity-20 tracking-widest"
              >
                {tab === "active" ? "✓ ALL CLEAR — NO ACTIVE ALERTS" : "NO RESOLVED ALERTS"}
              </motion.div>
            ) : (
              alerts.map((alert, index) => {
                const m = LEVEL_META[alert.level] || LEVEL_META.warning;
                // Ensure alertId is always unique and a string for React keys
                const alertId = alert.id || alert._id;
                let safeAlertId;
                
                if (typeof alertId === 'string' || typeof alertId === 'number') {
                  safeAlertId = String(alertId);
                } else {
                  safeAlertId = `alert-${index}-${Date.now()}`;
                }
                
                return (
                  <motion.div
                    key={safeAlertId}
                    layout
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20, height: 0 }}
                    transition={{ delay: index * 0.03 }}
                    className="rounded-xl p-4 flex items-start gap-4"
                    style={{ background: m.bg, border: `1px solid ${m.border}` }}
                  >
                    {/* Level badge */}
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                      style={{ background: `${m.color}18`, border: `1px solid ${m.color}30`, color: m.color }}
                    >
                      {m.icon}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-display font-bold text-sm" style={{ color: m.color }}>
                          {String(alert.level || "Unknown").toUpperCase()}
                        </span>
                        <span className="font-mono text-xs opacity-30">
                          PATIENT #{String(alert.patient_id || "N/A")}
                        </span>
                        <span className="font-mono text-xs opacity-30 ml-auto">
                          {alert.triggered_at ? new Date(alert.triggered_at).toLocaleString() : "N/A"}
                        </span>
                      </div>
                      <p className="font-mono text-xs text-white opacity-50 leading-relaxed">
                        {(() => {
                          const message = alert.message;
                          if (!message) return "No message available";
                          if (typeof message === "string") return message;
                          if (typeof message === "number") return String(message);
                          if (typeof message === "object") {
                            return JSON.stringify(message, null, 1).replace(/[\n\r]/g, ' ');
                          }
                          return String(message);
                        })()}
                      </p>
                      <div className="flex gap-3 mt-2">
                        <span className="font-mono text-xs opacity-20">
                          Nurse: {String(alert.nurse_notified) === "true" ? "✓ notified" : "✗ pending"}
                        </span>
                        <span className="font-mono text-xs opacity-20">
                          Doctor: {String(alert.doctor_notified) === "true" ? "✓ notified" : alert.level === "warning" ? "—" : "✗ pending"}
                        </span>
                      </div>
                    </div>

                    {tab === "active" && (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleResolve(alertId || alert.id || alert._id)}
                        disabled={resolving === (alertId || alert.id || alert._id)}
                        className="flex-shrink-0 px-3 py-1.5 rounded-lg font-mono text-xs tracking-widest transition-all"
                        style={{
                          background: "rgba(0,245,212,0.08)",
                          border: "1px solid rgba(0,245,212,0.2)",
                          color: "#00f5d4",
                          opacity: resolving === safeAlertId ? 0.5 : 1,
                        }}
                      >
                        {resolving === (alertId || alert.id || alert._id) ? "..." : "RESOLVE"}
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
