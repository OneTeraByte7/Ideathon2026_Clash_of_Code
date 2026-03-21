import { createContext, useContext, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const ToastCtx = createContext(null);

export function useToast() {
  return useContext(ToastCtx);
}

let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const toast = useCallback((message, level = "info", duration = 4000) => {
    const id = ++toastId;
    setToasts((t) => [...t, { id, message, level }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), duration);
  }, []);

  const LEVEL_STYLES = {
    info:     { color: "#00f5d4", bg: "rgba(0,245,212,0.08)",    border: "rgba(0,245,212,0.2)",   icon: "◉" },
    warning:  { color: "#f59e0b", bg: "rgba(245,158,11,0.1)",    border: "rgba(245,158,11,0.3)",  icon: "⚠" },
    critical: { color: "#ff2d78", bg: "rgba(255,45,120,0.1)",    border: "rgba(255,45,120,0.3)",  icon: "☠" },
    success:  { color: "#39ff14", bg: "rgba(57,255,20,0.08)",    border: "rgba(57,255,20,0.2)",   icon: "✓" },
  };

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div className="fixed bottom-6 right-6 z-[9998] flex flex-col gap-2 w-80">
        <AnimatePresence mode="popLayout">
          {toasts.map((t) => {
            const s = LEVEL_STYLES[t.level] || LEVEL_STYLES.info;
            return (
              <motion.div
                key={t.id}
                layout
                initial={{ opacity: 0, x: 60, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 60, scale: 0.95 }}
                transition={{ type: "spring", damping: 24, stiffness: 300 }}
                className="flex items-start gap-3 rounded-xl px-4 py-3"
                style={{ background: s.bg, border: `1px solid ${s.border}`, backdropFilter: "blur(12px)" }}
              >
                <span className="mt-0.5 flex-shrink-0" style={{ color: s.color }}>{s.icon}</span>
                <p className="font-mono text-xs leading-relaxed" style={{ color: "rgba(255,255,255,0.7)" }}>
                  {t.message}
                </p>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  );
}
