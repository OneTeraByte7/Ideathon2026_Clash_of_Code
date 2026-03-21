import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getTrend } from "../lib/api";
import RiskGauge from "./RiskGauge";
import VitalTile from "./VitalTile";

const CustomTooltip = ({ active, payload, isDark = true }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="rounded-lg px-3 py-2 font-mono text-xs" style={{ 
      background: isDark ? "#0d1220" : "#ffffff", 
      border: `1px solid ${isDark ? "rgba(0,245,212,0.2)" : "rgba(0,0,0,0.1)"}`, 
      color: isDark ? "#00f5d4" : "#06b6d4" 
    }}>
      <div className={`${isDark ? 'text-white' : 'text-gray-900'} opacity-50 mb-1`}>{new Date(d.payload.timestamp).toLocaleTimeString()}</div>
      <div>Risk: <span className="font-bold" style={{ color: d.value >= 70 ? "#ff2d78" : d.value >= 40 ? "#f59e0b" : isDark ? "#00f5d4" : "#06b6d4" }}>{d.value}</span></div>
    </div>
  );
};

export default function PatientDetail({ patient, onClose }) {
  const [trend, setTrend] = useState(null);
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    if (!patient) return;
    getTrend(patient.id, 20).then(setTrend).catch(() => {
      // Silently ignore trend fetch errors
    });
  }, [patient?.id]);

  useEffect(() => {
    const checkTheme = () => {
      setIsDark(document.body.classList.contains('light') === false);
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const level = patient?.risk_level || "normal";
  const accent = level === "critical" ? "#ff2d78" : level === "warning" ? "#f59e0b" : "#00f5d4";
  const vitals = patient?.vitals || {};

  const chartData = trend?.trend?.map((r) => ({
    timestamp: r.timestamp,
    score: r.risk_score,
    hr: r.heart_rate,
    lactate: r.lactate,
  })) || [];

  return (
    <AnimatePresence>
      {patient && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            style={{ background: "rgba(3,5,10,0.7)", backdropFilter: "blur(4px)" }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: "100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "100%", opacity: 0 }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-50 w-[520px] overflow-y-auto"
            style={{ 
              background: isDark ? "#080c14" : "#ffffff", 
              borderLeft: `1px solid ${isDark ? `${accent}22` : `${accent}44`}` 
            }}
          >
            {/* Top accent bar */}
            <div className="h-0.5 w-full" style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }} />

            <div className="p-7">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-5 right-5 w-8 h-8 flex items-center justify-center rounded-lg font-mono text-sm transition-all hover:opacity-70"
                style={{ 
                  background: isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.08)", 
                  color: isDark ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.5)", 
                  border: isDark ? "1px solid rgba(255,255,255,0.08)" : "1px solid rgba(0,0,0,0.1)" 
                }}
              >
                ✕
              </button>

              {/* Header */}
              <div className="flex items-center gap-5 mb-6">
                <RiskGauge score={patient.current_risk_score || 0} size={100} />
                <div>
                  <div className="font-mono text-xs tracking-widest mb-1" style={{ color: accent, opacity: 0.7 }}>
                    BED {patient.bed_number} · {patient.gender} · {patient.age}y
                  </div>
                  <h2 className={`font-display font-bold text-2xl ${isDark ? 'text-white' : 'text-gray-900'}`}>{patient.name}</h2>
                  <p className={`font-mono text-xs ${isDark ? 'opacity-40' : 'opacity-60'} mt-1`}>{patient.diagnosis}</p>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    {patient.allergies && (
                      <span className="font-mono text-xs px-2 py-0.5 rounded-full" style={{ background: "rgba(255,45,120,0.1)", color: "#ff2d78", border: "1px solid rgba(255,45,120,0.2)" }}>
                        ⚠ {patient.allergies}
                      </span>
                    )}
                    {patient.is_post_surgical && (
                      <span className="font-mono text-xs px-2 py-0.5 rounded-full" style={{ background: "rgba(245,158,11,0.1)", color: "#f59e0b", border: "1px solid rgba(245,158,11,0.2)" }}>
                        POST-SURGICAL
                      </span>
                    )}
                    {patient.is_immunocompromised && (
                      <span className="font-mono text-xs px-2 py-0.5 rounded-full" style={{ background: "rgba(255,45,120,0.1)", color: "#ff2d78", border: "1px solid rgba(255,45,120,0.2)" }}>
                        IMMUNOCOMP
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Vitals grid */}
              <div className="mb-6">
                <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-30' : 'opacity-50'} mb-3 uppercase`}>Current Vitals</div>
                <div className="grid grid-cols-3 gap-2">
                  {["heart_rate","systolic_bp","respiratory_rate","temperature","spo2","lactate"].map((k, i) => (
                    <VitalTile key={k} metricKey={k} value={vitals[k]} index={i} />
                  ))}
                </div>
              </div>

              {/* Trend chart */}
              <div className="mb-6">
                <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-30' : 'opacity-50'} mb-3 uppercase`}>Risk Score Trend</div>
                <div className="rounded-xl p-4" style={{ 
                  background: isDark ? "#0d1220" : "#f3f4f6", 
                  border: isDark ? "1px solid rgba(255,255,255,0.04)" : "1px solid rgba(0,0,0,0.1)" 
                }}>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={160}>
                      <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                        <defs>
                          <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={accent} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={accent} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="timestamp" tick={false} axisLine={false} tickLine={false} />
                        <YAxis domain={[0, 100]} tick={{ fill: isDark ? "rgba(255,255,255,0.2)" : "rgba(0,0,0,0.4)", fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                        <Tooltip content={<CustomTooltip isDark={isDark} />} />
                        <Area type="monotone" dataKey="score" stroke={accent} strokeWidth={2} fill="url(#scoreGrad)" dot={false} />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className={`h-40 flex items-center justify-center font-mono text-xs ${isDark ? 'opacity-20' : 'opacity-40'}`}>NO DATA YET</div>
                  )}
                </div>
              </div>

              {/* Active alerts */}
              {patient.active_alerts?.length > 0 && (
                <div>
                  <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-30' : 'opacity-50'} mb-3 uppercase`}>Active Alerts</div>
                  <div className="flex flex-col gap-2">
                    {patient.active_alerts.map((a, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="rounded-lg px-3 py-2 font-mono text-xs"
                        style={{
                          background: a.level === "critical" ? "rgba(255,45,120,0.08)" : "rgba(245,158,11,0.08)",
                          border: `1px solid ${a.level === "critical" ? "rgba(255,45,120,0.2)" : "rgba(245,158,11,0.2)"}`,
                          color: a.level === "critical" ? "#ff2d78" : "#f59e0b",
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: "currentColor" }} />
                          <span className="opacity-60">{a.message}</span>
                        </div>
                        <div className="mt-1 opacity-30 text-right">{new Date(a.at).toLocaleTimeString()}</div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
