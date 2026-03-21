import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { getPatients, getAlerts } from "../lib/api";
import { useICUStream } from "../hooks/useICUStream";
import PatientCard from "../components/PatientCard";
import PatientDetail from "../components/PatientDetail";
import SeedControl from "../components/SeedControl";
import StatsBar from "../components/StatsBar";
import CriticalBanner from "../components/CriticalBanner";

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("all");
  const [isDark, setIsDark] = useState(true);
  const { snapshot } = useICUStream();

  useEffect(() => {
    const checkTheme = () => {
      setIsDark(document.body.classList.contains('light') === false);
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const refresh = useCallback(async () => {
    try {
      const [p, a] = await Promise.all([getPatients(), getAlerts()]);
      setPatients(p);
      setAlerts(a);
    } catch {
      // Silently ignore errors
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Merge WS snapshot
  useEffect(() => {
    if (!snapshot?.patients) return;
    setPatients((prev) =>
      prev.map((p) => {
        const live = snapshot.patients.find((s) => s.id === p.id);
        if (!live) return p;
        return { ...p, current_risk_score: live.risk_score, risk_level: live.risk_level, vitals: live.vitals, active_alerts: live.active_alerts };
      })
    );
  }, [snapshot]);

  const FILTERS = ["all", "critical", "warning", "normal"];
  const FILTER_COLORS = { all: "#00f5d4", critical: "#ff2d78", warning: "#f59e0b", normal: "#39ff14" };

  const filtered = filter === "all" ? patients : patients.filter((p) => p.risk_level === filter);
  const sorted = [...filtered].sort((a, b) => {
    const order = { critical: 0, warning: 1, normal: 2 };
    return (order[a.risk_level] ?? 3) - (order[b.risk_level] ?? 3);
  });

  const criticalCount = patients.filter((p) => p.risk_level === "critical").length;
  const selectedPatient = patients.find((p) => p.id === selected) || null;

  return (
    <div className="min-h-screen grid-bg" style={{ paddingTop: "72px" }}>
      {/* Ambient orbs */}
      <div className="fixed top-32 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-[0.025] pointer-events-none" style={{ background: "#00f5d4" }} />
      <div className="fixed bottom-32 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-[0.025] pointer-events-none" style={{ background: "#ff2d78" }} />

      <CriticalBanner criticalCount={criticalCount} />

      <div className="max-w-screen-2xl mx-auto px-8 py-8">
        {/* Header with improved spacing */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-end justify-between mb-8"
        >
          <div>
            <h1 className={`font-display font-bold text-4xl ${isDark ? 'text-white' : 'text-gray-900'} tracking-tight mb-2`}>
              ICU Command
              <span className={`ml-3 font-mono text-sm font-normal ${isDark ? 'opacity-30' : 'opacity-40'} tracking-widest`}>CENTER</span>
            </h1>
            <p className={`font-mono text-xs ${isDark ? 'opacity-40' : 'opacity-60'} tracking-wide`}>{patients.length} patients monitored · Sepsis prediction active</p>
          </div>

          <div className="flex gap-2">
            {FILTERS.map((f) => {
              const count = f === "all" ? patients.length : patients.filter((p) => p.risk_level === f).length;
              return (
                <motion.button
                  key={f}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => setFilter(f)}
                  className="px-4 py-2 rounded-lg font-mono text-xs tracking-widest uppercase transition-all hover:shadow-lg"
                  style={{
                    background: filter === f ? `${FILTER_COLORS[f]}15` : isDark ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.03)",
                    border: `1px solid ${filter === f ? FILTER_COLORS[f] + "44" : isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.08)"}`,
                    color: filter === f ? FILTER_COLORS[f] : isDark ? "rgba(255,255,255,0.3)" : "rgba(0,0,0,0.4)",
                  }}
                >
                  {f} {count > 0 && <span className="opacity-50">({count})</span>}
                </motion.button>
              );
            })}
          </div>
        </motion.div>

        <StatsBar patients={patients} alerts={alerts} />

        <div className="grid grid-cols-12 gap-6">
          {/* Patient grid */}
          <div className="col-span-9">
            {sorted.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-72 rounded-2xl"
                style={{ 
                  border: isDark ? "1px dashed rgba(255,255,255,0.08)" : "1px dashed rgba(0,0,0,0.12)", 
                  background: isDark ? "rgba(13,18,32,0.5)" : "rgba(255,255,255,0.5)"
                }}
              >
                <div className={`text-5xl mb-4 ${isDark ? 'opacity-20' : 'opacity-15'}`}>⬡</div>
                <p className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-30' : 'opacity-40'} uppercase mb-1`}>No patients found</p>
                <p className={`font-mono text-xs ${isDark ? 'opacity-15' : 'opacity-30'}`}>Use scenario controls or seed patients via API</p>
              </motion.div>
            ) : (
              <div className="grid grid-cols-3 gap-5">
                {sorted.map((p, i) => (
                  <PatientCard
                    key={p.id}
                    patient={p}
                    index={i}
                    onClick={() => setSelected(p.id === selected ? null : p.id)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Right panel */}
          <div className="col-span-3 flex flex-col gap-5">
            <SeedControl onSeeded={refresh} />

            {/* Live alert feed */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl p-5 flex flex-col gap-4 flex-1" 
              style={{ 
                background: isDark ? "#0d1220" : "#ffffff",
                border: isDark ? "1px solid rgba(255,255,255,0.05)" : "1px solid rgba(0,0,0,0.08)"
              }}
            >
              <div className={`flex items-center justify-between pb-2 ${isDark ? 'border-white border-opacity-5' : 'border-gray-300 border-opacity-30'}`}>
                <span className={`font-display font-bold text-sm ${isDark ? 'text-white' : 'text-gray-900'} tracking-wide`}>LIVE ALERTS</span>
                <span className="font-mono text-xs px-3 py-1 rounded-full" style={{ background: "rgba(255,45,120,0.12)", color: "#ff2d78", border: "1px solid rgba(255,45,120,0.25)" }}>
                  {alerts.filter(a => !a.resolved).length} active
                </span>
              </div>

              <div className="flex flex-col gap-3 overflow-y-auto flex-1 pr-2">
                {alerts.filter(a => !a.resolved).length === 0 ? (
                  <div className={`text-center py-8 font-mono text-xs ${isDark ? 'opacity-25' : 'opacity-40'}`}>✓ ALL CLEAR</div>
                ) : (
                  alerts.filter(a => !a.resolved).slice(0, 8).map((a, i) => {
                    const color = a.level === "critical" ? "#ff2d78" : "#f59e0b";
                    return (
                      <motion.div
                        key={a.id || i}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.04 }}
                        className="rounded-lg px-4 py-3 hover:bg-opacity-20 transition-all"
                        style={{ background: `${color}0f`, border: `1px solid ${color}25` }}
                      >
                        <div className="flex items-center gap-2.5 mb-1.5">
                          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
                          <span className="font-mono text-xs font-bold tracking-widest" style={{ color }}>
                            {a.level?.toUpperCase()}
                          </span>
                          <span className="font-mono text-xs opacity-40 ml-auto">
                            {new Date(a.triggered_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                        <p className="font-mono text-xs opacity-50 leading-relaxed pl-4">{a.message}</p>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <PatientDetail patient={selectedPatient} onClose={() => setSelected(null)} />
    </div>
  );
}
