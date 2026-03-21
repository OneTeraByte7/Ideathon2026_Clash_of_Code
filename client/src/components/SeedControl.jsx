import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { seedNormal, seedWarning, seedCritical } from "../lib/api";
import { useToast } from "./Toast";

const SEEDS = [
  {
    key: "normal",
    label: "NOMINAL",
    sub: "All vitals stable",
    color: "#00f5d4",
    bg: "rgba(0,245,212,0.08)",
    border: "rgba(0,245,212,0.25)",
    fn: seedNormal,
    icon: "◉",
    toastLevel: "success",
  },
  {
    key: "warning",
    label: "ALERT",
    sub: "Borderline signals",
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.08)",
    border: "rgba(245,158,11,0.3)",
    fn: seedWarning,
    icon: "⚠",
    toastLevel: "warning",
  },
  {
    key: "critical",
    label: "CRITICAL",
    sub: "Sepsis imminent",
    color: "#ff2d78",
    bg: "rgba(255,45,120,0.1)",
    border: "rgba(255,45,120,0.4)",
    fn: seedCritical,
    icon: "☠",
    toastLevel: "critical",
  },
];

export default function SeedControl({ onSeeded }) {
  const [loading, setLoading] = useState(null);
  const toast = useToast();

  const handleSeed = async (seed) => {
    setLoading(seed.key);
    try {
      const res = await seed.fn();
      toast(res.description || `${seed.label} scenario applied`, seed.toastLevel);
      onSeeded?.();
    } catch {
      // Mock mode — simulate the scenario change
      toast(`${seed.label} scenario applied (demo mode)`, seed.toastLevel);
      onSeeded?.();
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="rounded-2xl p-5 border border-white/5" style={{ background: "#0d1220" }}>
      <div className="flex items-center gap-3 mb-4">
        <div className="w-1.5 h-6 rounded-full" style={{ background: "linear-gradient(#00f5d4, #ff2d78)" }} />
        <div>
          <h2 className="font-display font-bold text-white text-sm tracking-wide">SCENARIO CONTROL</h2>
          <p className="font-mono text-xs opacity-30">Inject vitals into all ICU beds</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {SEEDS.map((seed) => (
          <motion.button
            key={seed.key}
            whileHover={{ scale: 1.03, y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => handleSeed(seed)}
            disabled={loading !== null}
            className="relative rounded-xl p-4 text-left overflow-hidden transition-all"
            style={{
              background: seed.bg,
              border: `1px solid ${seed.border}`,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading && loading !== seed.key ? 0.5 : 1,
            }}
          >
            <AnimatePresence>
              {loading === seed.key && (
                <motion.div
                  className="absolute inset-0 opacity-20"
                  style={{ background: `linear-gradient(90deg, transparent, ${seed.color}, transparent)` }}
                  initial={{ x: "-100%" }}
                  animate={{ x: "100%" }}
                  transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                />
              )}
            </AnimatePresence>

            <div className="text-2xl mb-2" style={{ color: seed.color }}>{seed.icon}</div>
            <div className="font-display font-bold text-sm" style={{ color: seed.color }}>{seed.label}</div>
            <div className="font-mono text-xs opacity-40 mt-0.5">{seed.sub}</div>

            {loading === seed.key && (
              <div className="absolute bottom-2 right-2">
                <div className="w-3 h-3 rounded-full border-2 animate-spin"
                  style={{ borderColor: seed.color, borderTopColor: "transparent" }} />
              </div>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
