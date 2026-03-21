import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const ToastCtx = createContext(null);

export function useToast() {
  return useContext(ToastCtx);
}

let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
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

  const toast = useCallback((message, level = "info", duration = 4000) => {
    const id = ++toastId;
    setToasts((t) => [...t, { id, message, level }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), duration);
  }, []);

  const LEVEL_STYLES = {
    info:     { color: "#00f5d4", colorLight: "#06b6d4", bg: "rgba(0,245,212,0.08)", bgLight: "rgba(6,182,212,0.1)",    border: "rgba(0,245,212,0.2)", borderLight: "rgba(6,182,212,0.25)",   icon: "◉" },
    warning:  { color: "#f59e0b", colorLight: "#eab308", bg: "rgba(245,158,11,0.1)", bgLight: "rgba(234,179,8,0.12)",    border: "rgba(245,158,11,0.3)", borderLight: "rgba(234,179,8,0.35)",  icon: "⚠" },
    critical: { color: "#ff2d78", colorLight: "#ec4899", bg: "rgba(255,45,120,0.1)", bgLight: "rgba(236,72,153,0.12)",    border: "rgba(255,45,120,0.3)", borderLight: "rgba(236,72,153,0.35)",  icon: "☠" },
    success:  { color: "#39ff14", colorLight: "#84cc16", bg: "rgba(57,255,20,0.08)", bgLight: "rgba(132,204,22,0.1)",    border: "rgba(57,255,20,0.2)", borderLight: "rgba(132,204,22,0.3)",   icon: "✓" },
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
                style={{
                  background: isDark ? s.bg : s.bgLight,
                  border: `1px solid ${isDark ? s.border : s.borderLight}`,
                  backdropFilter: "blur(12px)"
                }}
              >
                <span className="mt-0.5 flex-shrink-0" style={{ color: isDark ? s.color : s.colorLight }}>
                  {s.icon}
                </span>
                <p className={`font-mono text-xs leading-relaxed ${isDark ? 'text-white' : 'text-gray-900'}`} style={{ opacity: isDark ? 0.7 : 0.8 }}>
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
