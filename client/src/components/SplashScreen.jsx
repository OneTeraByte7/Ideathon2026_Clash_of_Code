import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

const BOOT_LINES = [
  "INITIALIZING ASCLEPIUS AI v1.0.0",
  "LOADING SEPSIS PREDICTION ENGINE...",
  "CONNECTING TO ICU DATA STREAM...",
  "MULTI-AGENT SYSTEM ONLINE",
  "GEMINI 2.0 FLASH THINKING READY",
  "ALL SYSTEMS NOMINAL",
];

export default function SplashScreen({ onComplete }) {
  const [lines, setLines] = useState([]);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < BOOT_LINES.length) {
        setLines((prev) => [...prev, BOOT_LINES[i]]);
        i++;
      } else {
        clearInterval(interval);
        setTimeout(() => setDone(true), 500);
        setTimeout(() => onComplete?.(), 1200);
      }
    }, 280);
    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {!done ? (
        <motion.div
          exit={{ opacity: 0, scale: 1.04 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
          style={{ background: "#03050a" }}
        >
          {/* Grid bg */}
          <div className="absolute inset-0 grid-bg opacity-40" />

          {/* Ambient glow orbs */}
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl opacity-[0.04]" style={{ background: "#00f5d4" }} />

          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="relative mb-12 flex flex-col items-center"
          >
            {/* Outer ring */}
            <div className="relative w-24 h-24 mb-6">
              <svg viewBox="0 0 96 96" className="w-24 h-24 animate-spin" style={{ animationDuration: "12s" }}>
                <circle cx="48" cy="48" r="44" fill="none" stroke="rgba(0,245,212,0.15)" strokeWidth="1" strokeDasharray="4 6" />
              </svg>
              <svg viewBox="0 0 96 96" className="absolute inset-0 w-24 h-24">
                <circle cx="48" cy="48" r="36" fill="none" stroke="rgba(0,245,212,0.3)" strokeWidth="1" />
                <circle cx="48" cy="48" r="24" fill="none" stroke="rgba(0,245,212,0.5)" strokeWidth="1.5" />
                {/* ECG path */}
                <path
                  d="M28 48 L36 48 L38 48 L40 36 L42 60 L44 48 L52 48 L54 48 L56 40 L58 56 L60 48 L68 48"
                  fill="none" stroke="#00f5d4" strokeWidth="2" strokeLinecap="round"
                  style={{ filter: "drop-shadow(0 0 4px #00f5d4)" }}
                />
              </svg>
              {/* Center pulse */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full" style={{ background: "#00f5d4", boxShadow: "0 0 12px #00f5d4, 0 0 30px rgba(0,245,212,0.4)" }} />
              </div>
            </div>

            <div className="text-center">
              <div className="font-display font-bold text-4xl text-white tracking-[0.2em] mb-1" style={{ textShadow: "0 0 40px rgba(255,255,255,0.1)" }}>
                ASCLEPIUS
              </div>
              <div className="font-mono text-xs tracking-[0.4em]" style={{ color: "#00f5d4", opacity: 0.7 }}>
                AI · ICU COMMAND SYSTEM
              </div>
            </div>
          </motion.div>

          {/* Boot console */}
          <div className="w-80 rounded-xl p-5 font-mono text-xs" style={{ background: "rgba(13,18,32,0.8)", border: "1px solid rgba(0,245,212,0.1)" }}>
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-white/5">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: "#ff2d78" }} />
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: "#f59e0b" }} />
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: "#39ff14" }} />
              </div>
              <span className="opacity-20">asclepius_boot.sh</span>
            </div>

            <div className="flex flex-col gap-1.5 min-h-[120px]">
              {lines.map((line, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-2"
                >
                  <span style={{ color: "#00f5d4", opacity: 0.5 }}>›</span>
                  <span style={{ color: i === lines.length - 1 ? "#00f5d4" : "rgba(255,255,255,0.4)" }}>
                    {line}
                  </span>
                  {i === lines.length - 1 && (
                    <span className="inline-block w-1.5 h-3 ml-0.5 animate-pulse" style={{ background: "#00f5d4" }} />
                  )}
                </motion.div>
              ))}
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-80 mt-4 h-0.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
            <motion.div
              className="h-full rounded-full"
              style={{ background: "linear-gradient(90deg, #00f5d4, #38bdf8)", boxShadow: "0 0 8px #00f5d4" }}
              initial={{ width: "0%" }}
              animate={{ width: `${(lines.length / BOOT_LINES.length) * 100}%` }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            />
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
