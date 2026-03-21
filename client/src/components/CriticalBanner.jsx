import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

export default function CriticalBanner({ criticalCount }) {
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

  return (
    <AnimatePresence>
      {criticalCount > 0 && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="overflow-hidden"
        >
          <div
            className="flex items-center justify-between px-6 py-2.5 mb-4"
            style={{
              background: isDark ? "rgba(255,45,120,0.08)" : "rgba(236,72,153,0.06)",
              borderTop: isDark ? "1px solid rgba(255,45,120,0.2)" : "1px solid rgba(236,72,153,0.25)",
              borderBottom: isDark ? "1px solid rgba(255,45,120,0.2)" : "1px solid rgba(236,72,153,0.25)",
              animation: "criticalBorder 1.5s ease-in-out infinite",
            }}
          >
            <div className="flex items-center gap-3">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pulse opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-pulse" />
              </span>
              <span className="font-mono text-xs tracking-widest" style={{ color: isDark ? "#ff2d78" : "#ec4899" }}>
                SEPSIS ALERT ACTIVE
              </span>
              <span className="font-mono text-xs opacity-50" style={{ color: isDark ? "#ff2d78" : "#ec4899" }}>
                {criticalCount} patient{criticalCount !== 1 ? "s" : ""} in critical state
              </span>
            </div>
            <span className="font-mono text-xs opacity-30" style={{ color: isDark ? "#ff2d78" : "#ec4899" }}>
              GEMINI PROTOCOL GENERATED · AWAITING DOCTOR REVIEW
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
