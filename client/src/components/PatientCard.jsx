import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import RiskGauge from "./RiskGauge";
import VitalTile from "./VitalTile";
import ECGLine from "./ECGLine";
import { triggerCriticalAlert } from "../lib/api";

const LEVEL_STYLES = {
  normal:   { accent: "#00f5d4", label: "STABLE",   bg: "rgba(0,245,212,0.03)" },
  warning:  { accent: "#f59e0b", label: "WARNING",  bg: "rgba(245,158,11,0.05)" },
  critical: { accent: "#ff2d78", label: "CRITICAL", bg: "rgba(255,45,120,0.06)" },
};

export default function PatientCard({ patient, onClick, index = 0 }) {
  const [hovered, setHovered] = useState(false);
  const [isDark, setIsDark] = useState(true);
  const [alertSending, setAlertSending] = useState(false);
  const level = patient.risk_level || "normal";
  const s = LEVEL_STYLES[level];
  const vitals = patient.vitals || {};
  const isCritical = level === "critical";
  const isWarning = level === "warning";

  useEffect(() => {
    const checkTheme = () => {
      setIsDark(document.body.classList.contains('light') === false);
    };
    checkTheme();
    const observer = new MutationObserver(checkTheme);
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const handleCriticalAlert = async (e) => {
    e.stopPropagation(); // Prevent card click
    setAlertSending(true);
    
    try {
      const result = await triggerCriticalAlert(patient.id);
      alert(`✅ ${result.message}`);
    } catch (error) {
      alert("❌ Failed to send critical alert");
    } finally {
      setAlertSending(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      onClick={onClick}
      className="relative rounded-2xl cursor-pointer overflow-hidden hover:shadow-lg transition-all"
      style={{
        background: isDark ? `linear-gradient(135deg, #0d1220, ${s.bg})` : `linear-gradient(135deg, #ffffff, rgba(248,250,251,0.8))`,
        border: `1px solid ${s.accent}22`,
        animation: isCritical ? "criticalBorder 1.5s ease-in-out infinite"
                 : isWarning  ? "warnBorder 2s ease-in-out infinite"
                 : "borderPulse 3s ease-in-out infinite",
      }}
    >
      {/* Glow corner */}
      <div
        className="absolute -top-10 -right-10 w-40 h-40 rounded-full blur-3xl opacity-25"
        style={{ background: s.accent }}
      />

      {/* Critical alert bar */}
      <AnimatePresence>
        {isCritical && (
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            className="absolute top-0 left-0 right-0 h-1"
            style={{ background: `linear-gradient(90deg, transparent, ${s.accent}, transparent)`, transformOrigin: "left" }}
          />
        )}
      </AnimatePresence>

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-5">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span
                className="font-mono text-xs tracking-widest px-3 py-1 rounded-lg font-semibold"
                style={{ color: s.accent, background: `${s.accent}18`, border: `1px solid ${s.accent}33` }}
              >
                BED {patient.bed_number}
              </span>
              {isCritical && (
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pulse opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-pulse" />
                </span>
              )}
            </div>
            <h3 className={`font-display font-bold text-lg ${isDark ? 'text-white' : 'text-gray-900'} leading-tight mb-1`}>{patient.name}</h3>
            <p className={`text-xs ${isDark ? 'opacity-50' : 'opacity-60'} font-mono truncate max-w-[160px]`}>{patient.diagnosis}</p>
          </div>

          <RiskGauge score={patient.current_risk_score || 0} size={92} />
        </div>

        {/* ECG strip */}
        <div className="mb-5 opacity-70">
          <ECGLine
            color={s.accent}
            height={40}
          />
        </div>

        {/* Vitals grid */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {["heart_rate", "systolic_bp", "respiratory_rate", "temperature", "spo2", "lactate"].map((key, i) => (
            <VitalTile key={key} metricKey={key} value={vitals[key]} index={i} />
          ))}
        </div>

        {/* Alert badges */}
        {patient.active_alerts?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="pt-3 border-t border-white/5 mb-3"
          >
            {patient.active_alerts.slice(0, 1).map((a, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <span className="w-2 h-2 rounded-full flex-shrink-0 mt-0.5" style={{ background: s.accent }} />
                <p className="text-xs opacity-60 font-mono truncate">{a.message}</p>
              </div>
            ))}
          </motion.div>
        )}

        {/* Critical Alert Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleCriticalAlert}
          disabled={alertSending}
          className="w-full py-2 px-3 rounded-lg font-mono text-xs font-bold tracking-widest transition-all flex items-center justify-center gap-2"
          style={{
            background: isCritical ? "#ff2d7820" : "#ff2d7810",
            border: "1px solid #ff2d7830",
            color: "#ff2d78",
          }}
        >
          {alertSending ? (
            <>
              <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
              SENDING...
            </>
          ) : (
            <>
              🚨 TRIGGER CRITICAL ALERT
            </>
          )}
        </motion.button>
      </div>

      {/* Hover expand hint */}
      <AnimatePresence>
        {hovered && !alertSending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute bottom-4 right-5 font-mono text-xs tracking-widest opacity-50 font-semibold"
            style={{ color: s.accent }}
          >
            VIEW DETAILS →
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
