import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { RadialBarChart, RadialBar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";
import { getAccuracy, getPatients } from "../lib/api";

const CustomTooltip = ({ active, payload, isDark = true }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg px-3 py-2 font-mono text-xs" style={{ 
      background: isDark ? "#0d1220" : "#ffffff", 
      border: isDark ? "1px solid rgba(0,245,212,0.2)" : "1px solid rgba(0,0,0,0.1)", 
      color: isDark ? "#00f5d4" : "#06b6d4" 
    }}>
      {payload[0].name}: <span className="font-bold">{payload[0].value}</span>
    </div>
  );
};

export default function AnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [patients, setPatients] = useState([]);
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

  useEffect(() => {
    getAccuracy().then(setStats).catch(() => {
      // Silently ignore accuracy fetch errors
    });
    getPatients().then(setPatients).catch(() => {
      // Silently ignore patients fetch errors
    });
  }, []);

  if (!stats) {
    return (
      <div className="min-h-screen grid-bg flex items-center justify-center" style={{ paddingTop: "72px" }}>
        <div className="font-mono text-xs tracking-widest opacity-20 animate-pulse">LOADING ANALYTICS...</div>
      </div>
    );
  }

  const alertDist = [
    { name: "Critical", value: stats.critical_alerts, color: "#ff2d78" },
    { name: "Warning",  value: stats.warning_alerts,  color: "#f59e0b" },
  ];

  const patientRisk = patients.map((p) => ({
    name: p.bed_number,
    score: Math.round(p.current_risk_score || 0),
    level: p.risk_level,
  }));

  const radialData = [
    { name: "Critical", value: stats.critical_alerts, fill: "#ff2d78" },
    { name: "Warning",  value: stats.warning_alerts,  fill: "#f59e0b" },
    { name: "Total",    value: stats.total_alerts,     fill: "#00f5d4" },
  ];

  const metricCards = [
    { label: "TOTAL ALERTS",        value: stats.total_alerts,           color: "#00f5d4" },
    { label: "CRITICAL EVENTS",     value: stats.critical_alerts,        color: "#ff2d78" },
    { label: "AVG RISK AT ALERT",   value: `${stats.average_risk_score_at_alert}`, color: "#f59e0b", unit: "/100" },
    { label: "HIGH CONFIDENCE",     value: stats.high_confidence_alerts, color: "#39ff14", sub: "score ≥80" },
  ];

  return (
    <div className="min-h-screen grid-bg" style={{ paddingTop: "72px" }}>
      <div className="max-w-screen-xl mx-auto px-8 py-10">

        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className={`font-display font-bold text-4xl ${isDark ? 'text-white' : 'text-gray-900'} mb-2`}>Analytics</h1>
          <p className={`font-mono text-xs ${isDark ? 'opacity-40' : 'opacity-60'} tracking-wide`}>LEARNING AGENT · PREDICTION ACCURACY · SYSTEM PERFORMANCE</p>
        </motion.div>

        {/* Metric cards */}
        <div className="grid grid-cols-4 gap-5 mb-10">
          {metricCards.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="rounded-2xl p-6 hover:shadow-lg transition-all"
              style={{ 
                background: isDark ? "#0d1220" : "#f3f4f6", 
                border: isDark ? `1px solid ${m.color}1a` : `1px solid ${m.color}33` 
              }}
            >
              <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-40' : 'opacity-60'} mb-3`}>{m.label}</div>
              <div className="font-display font-bold text-4xl leading-none" style={{ color: m.color, textShadow: `0 0 30px ${m.color}66` }}>
                {m.value}
                {m.unit && <span className="text-lg opacity-60 ml-1">{m.unit}</span>}
              </div>
              {m.sub && <div className={`font-mono text-xs ${isDark ? 'opacity-30' : 'opacity-50'} mt-2`}>{m.sub}</div>}
            </motion.div>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-12 gap-6 mb-8">
          {/* Patient risk bar chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-7 rounded-2xl p-6 hover:shadow-lg transition-all"
            style={{ 
              background: isDark ? "#0d1220" : "#f3f4f6", 
              border: isDark ? "1px solid rgba(255,255,255,0.05)" : "1px solid rgba(0,0,0,0.1)" 
            }}
          >
            <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-40' : 'opacity-60'} mb-5 uppercase font-semibold`}>Current Risk Score — All Patients</div>
            {patientRisk.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={patientRisk} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
                  <XAxis dataKey="name" tick={{ fill: isDark ? "rgba(255,255,255,0.35)" : "rgba(0,0,0,0.5)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: isDark ? "rgba(255,255,255,0.25)" : "rgba(0,0,0,0.4)", fontSize: 11, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip isDark={isDark} />} cursor={{ fill: isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)" }} />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]} isAnimationActive={true}>
                    {patientRisk.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={entry.level === "critical" ? "#ff2d78" : entry.level === "warning" ? "#f59e0b" : "#00f5d4"}
                        opacity={0.9}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className={`h-56 flex items-center justify-center font-mono text-xs ${isDark ? 'opacity-30' : 'opacity-40'}`}>NO PATIENT DATA</div>
            )}
          </motion.div>

          {/* Radial distribution */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="col-span-5 rounded-2xl p-6 hover:shadow-lg transition-all"
            style={{ 
              background: isDark ? "#0d1220" : "#f3f4f6", 
              border: isDark ? "1px solid rgba(255,255,255,0.05)" : "1px solid rgba(0,0,0,0.1)" 
            }}
          >
            <div className={`font-mono text-xs tracking-widest ${isDark ? 'opacity-40' : 'opacity-60'} mb-5 uppercase font-semibold`}>Alert Distribution</div>
            <ResponsiveContainer width="100%" height={180}>
              <RadialBarChart cx="50%" cy="50%" innerRadius="30%" outerRadius="90%" data={radialData} startAngle={90} endAngle={-270}>
                <RadialBar dataKey="value" cornerRadius={6} isAnimationActive={true} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-4">
              {alertDist.map((d) => (
                <div key={d.name} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                  <span className={`font-mono text-xs ${isDark ? 'opacity-50' : 'opacity-60'} font-semibold`}>{d.name}: {d.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Insights */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-2xl p-6 hover:shadow-lg transition-all"
          style={{ background: "#0d1220", border: "1px solid rgba(0,245,212,0.1)" }}
        >
          <div className="flex items-center gap-2 mb-5 pb-3 border-b border-white border-opacity-5">
            <span style={{ color: "#00f5d4", fontSize: "1.2em" }}>◉</span>
            <span className="font-mono text-xs tracking-widest opacity-40 uppercase font-semibold">Learning Agent Insights</span>
          </div>
          <div className="flex flex-col gap-3">
            {(stats.insights || ["No insights yet."]).map((insight, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + i * 0.07 }}
                className="flex items-start gap-3"
              >
                <div className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 bg-gradient-to-br" style={{ background: "#00f5d4" }} />
                <p className="font-mono text-xs text-white opacity-60 leading-relaxed">{insight}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
