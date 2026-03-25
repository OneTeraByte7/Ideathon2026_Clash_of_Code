import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { getPatients, getAlerts } from "../lib/api";
import { useICUStream } from "../hooks/useICUStream";
import PatientCard from "../components/PatientCard";
import PatientDetail from "../components/PatientDetail";
import SeedControl from "../components/SeedControl";
import ThrottleControl from "../components/ThrottleControl";
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
      // Ensure we always have clean arrays with valid objects
      const validPatients = Array.isArray(p) ? p.filter(patient => patient && typeof patient === 'object' && patient.id) : [];
      const validAlerts = Array.isArray(a) ? a.filter(alert => alert && typeof alert === 'object') : [];
      
      setPatients(validPatients);
      setAlerts(validAlerts);
    } catch {
      // Silently ignore errors but ensure we have arrays
      setPatients(prev => Array.isArray(prev) ? prev : []);
      setAlerts(prev => Array.isArray(prev) ? prev : []);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Enhanced WebSocket data processing with better error handling
  useEffect(() => {
    if (!snapshot?.patients || !Array.isArray(snapshot.patients)) return;
    
    setPatients((prev) => {
      // Ensure prev is always an array
      const validPrev = Array.isArray(prev) ? prev : [];
      
      return validPrev.map((p) => {
        // Skip invalid patient objects
        if (!p || typeof p !== 'object' || !p.id) return p;
        
        const live = snapshot.patients.find((s) => s && s.id === p.id);
        if (!live) return p;
        
        // Safely merge live data
        return { 
          ...p, 
          current_risk_score: live.risk_score ?? p.current_risk_score, 
          risk_level: live.risk_level || p.risk_level, 
          vitals: live.vitals || p.vitals, 
          active_alerts: Array.isArray(live.active_alerts) ? live.active_alerts : (p.active_alerts || [])
        };
      }).filter(p => p && p.id); // Remove any invalid entries
    });
  }, [snapshot]);

  const FILTERS = ["all", "critical", "warning", "normal"];
  const FILTER_COLORS = { all: "#00f5d4", critical: "#ff2d78", warning: "#f59e0b", normal: "#39ff14" };

  // Ensure we always work with valid data
  const validPatients = Array.isArray(patients) ? patients.filter(p => p && typeof p === 'object' && p.id) : [];
  const validAlerts = Array.isArray(alerts) ? alerts.filter(a => a && typeof a === 'object') : [];
  
  const filtered = filter === "all" ? validPatients : validPatients.filter((p) => p.risk_level === filter);
  const sorted = [...filtered].sort((a, b) => {
    const order = { critical: 0, warning: 1, normal: 2 };
    return (order[a.risk_level] ?? 3) - (order[b.risk_level] ?? 3);
  });

  const criticalCount = validPatients.filter((p) => p.risk_level === "critical").length;
  const selectedPatient = validPatients.find((p) => p.id === selected) || null;

  return (
    <div className={`min-h-screen grid-bg transition-colors duration-300 ${
      isDark ? '' : 'bg-gray-50'
    }`} style={{ paddingTop: "72px" }}>
      {/* Ambient orbs */}
      <div className={`fixed top-32 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-[0.025] pointer-events-none`} 
        style={{ background: isDark ? "#00f5d4" : "#06b6d4" }} />
      <div className={`fixed bottom-32 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-[0.025] pointer-events-none`} 
        style={{ background: isDark ? "#ff2d78" : "#ec4899" }} />

      <CriticalBanner criticalCount={criticalCount} />

      <div className="max-w-screen-2xl mx-auto px-6 py-6">
        {/* Header with improved spacing */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-end justify-between mb-6"
        >
          <div>
            <h1 className={`font-display font-bold text-3xl ${isDark ? 'text-white' : 'text-gray-900'} tracking-tight mb-1`}>
              ICU Command
              <span className={`ml-3 font-mono text-sm font-normal ${isDark ? 'opacity-30' : 'opacity-40'} tracking-widest`}>CENTER</span>
            </h1>
            <p className={`font-mono text-xs ${isDark ? 'opacity-40' : 'opacity-60'} tracking-wide`}>{validPatients.length} patients monitored · Sepsis prediction active</p>
          </div>

          <div className="flex gap-2">
            {FILTERS.map((f) => {
              const count = f === "all" ? validPatients.length : validPatients.filter((p) => p.risk_level === f).length;
              return (
                <motion.button
                  key={f}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => setFilter(f)}
                  className="px-3 py-2 rounded-lg font-mono text-xs tracking-widest uppercase transition-all hover:shadow-lg"
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

        <StatsBar patients={validPatients} alerts={validAlerts} />

        <div className="grid grid-cols-12 gap-5">
          {/* Patient grid */}
          <div className="col-span-9">
            {sorted.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-64 rounded-2xl"
                style={{ 
                  border: isDark ? "1px dashed rgba(255,255,255,0.08)" : "1px dashed rgba(0,0,0,0.12)", 
                  background: isDark ? "rgba(13,18,32,0.5)" : "rgba(255,255,255,0.5)"
                }}
              >
                <div className={`text-4xl mb-3 ${isDark ? 'opacity-20' : 'opacity-15'}`}>⬡</div>
                <p className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-30' : 'opacity-40'} uppercase mb-1`}>No patients found</p>
                <p className={`font-mono text-xs ${isDark ? 'opacity-15' : 'opacity-30'}`}>Use scenario controls or seed patients via API</p>
              </motion.div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                {sorted.map((p, i) => {
                  // Triple-check we have a valid patient
                  if (!p || typeof p !== 'object' || !p.id) {
                    console.warn('Invalid patient in sorted array:', p);
                    return null;
                  }
                  
                  // Create absolutely unique key with multiple fallbacks  
                  const patientKey = `patient-${String(p.id)}-${p.name?.replace(/\s+/g, '-') || 'unknown'}-${i}`;
                  
                  return (
                    <PatientCard
                      key={patientKey}
                      patient={p}
                      index={i}
                      onClick={() => setSelected(p.id === selected ? null : p.id)}
                    />
                  );
                }).filter(Boolean)} {/* Remove any null entries */}
              </div>
            )}
          </div>

          {/* Right panel */}
          <div className="col-span-3 flex flex-col gap-4">
            <SeedControl onSeeded={refresh} />
            <ThrottleControl />

            {/* Live alert feed */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl p-4 flex flex-col gap-3 flex-1" 
              style={{ 
                background: isDark ? "#0d1220" : "#ffffff",
                border: isDark ? "1px solid rgba(255,255,255,0.05)" : "1px solid rgba(0,0,0,0.08)"
              }}
            >
              <div className={`flex items-center justify-between pb-2 border-b ${isDark ? 'border-white border-opacity-5' : 'border-gray-300 border-opacity-30'}`}>
                <span className={`font-display font-bold text-sm ${isDark ? 'text-white' : 'text-gray-900'} tracking-wide`}>LIVE ALERTS</span>
                <span className="font-mono text-xs px-2.5 py-1 rounded-full" style={{ background: "rgba(255,45,120,0.12)", color: "#ff2d78", border: "1px solid rgba(255,45,120,0.25)" }}>
                  {validAlerts.filter(a => a && !a.resolved).length} active
                </span>
              </div>

              <div className="flex flex-col gap-2.5 overflow-y-auto flex-1 pr-2">
                {validAlerts.filter(a => a && !a.resolved).length === 0 ? (
                  <div className={`text-center py-6 font-mono text-xs ${isDark ? 'opacity-25' : 'opacity-40'}`}>✓ ALL CLEAR</div>
                ) : (
                  validAlerts.filter(a => a && !a.resolved).slice(0, 8).map((a, i) => {
                    // Skip invalid alert objects
                    if (!a || typeof a !== 'object') {
                      console.warn('Invalid alert:', a);
                      return null;
                    }
                    
                    const color = a.level === "critical" ? "#ff2d78" : "#f59e0b";
                    // Create unique alert key with timestamp and content - avoid object references
                    const alertKey = `alert-${i}-${a.level || 'unknown'}-${a.triggered_at || Date.now()}-${String(a.message || 'msg').substring(0, 10)}`;
                    
                    return (
                      <motion.div
                        key={alertKey}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.04 }}
                        className="rounded-lg px-3 py-2.5 hover:bg-opacity-20 transition-all"
                        style={{ background: `${color}0f`, border: `1px solid ${color}25` }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
                          <span className="font-mono text-xs font-bold tracking-widest" style={{ color }}>
                            {String(a.level || 'UNKNOWN').toUpperCase()}
                          </span>
                          <span className={`font-mono text-xs opacity-40 ml-auto ${isDark ? 'text-white' : 'text-gray-600'}`}>
                            {a.triggered_at ? new Date(a.triggered_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : '--:--'}
                          </span>
                        </div>
                        <p className={`font-mono text-xs opacity-50 leading-relaxed pl-4 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                          {String(a.message || 'No message')}
                        </p>
                      </motion.div>
                    );
                  }).filter(Boolean) // Remove any null entries
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
