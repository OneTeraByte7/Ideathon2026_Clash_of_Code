import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_LINKS = [
  { path: "/",          label: "ICU GRID",   icon: "⬡" },
  { path: "/alerts",    label: "ALERTS",     icon: "◈" },
  { path: "/protocols", label: "PROTOCOLS",  icon: "⊕" },
  { path: "/analytics", label: "ANALYTICS",  icon: "≋" },
];

export default function Navbar({ connected }) {
  const location = useLocation();
  const [time, setTime] = useState(new Date());
  const [theme, setTheme] = useState(() => localStorage.getItem("asclepius-theme") || "dark");

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    // Apply theme class to body when component mounts or theme changes
    document.body.className = theme === "light" ? "light" : "";
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("asclepius-theme", newTheme);
    document.body.className = newTheme === "light" ? "light" : "";
  };

  const hh = time.getHours().toString().padStart(2, "0");
  const mm = time.getMinutes().toString().padStart(2, "0");
  const ss = time.getSeconds().toString().padStart(2, "0");

  const isDark = theme === "dark";

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-3"
      style={{
        background: isDark 
          ? "rgba(8,12,20,0.85)" 
          : "rgba(248,250,252,0.90)",
        backdropFilter: "blur(24px)",
        borderBottom: isDark 
          ? "1px solid rgba(0,245,212,0.08)" 
          : "1px solid rgba(6,182,212,0.15)",
      }}
    >
      {/* Logo */}
      <Link to="/" className="flex items-center gap-3 group">
        <div className="relative w-8 h-8">
          <svg viewBox="0 0 32 32" className="w-8 h-8">
            <circle cx="16" cy="16" r="14" fill="none" 
              stroke={isDark ? "#00f5d4" : "#06b6d4"} 
              strokeWidth="1.5" opacity="0.4" />
            <circle cx="16" cy="16" r="9" fill="none" 
              stroke={isDark ? "#00f5d4" : "#06b6d4"} 
              strokeWidth="1" opacity="0.6" />
            <path d="M8 16 L13 16 L15 11 L17 21 L19 16 L24 16" fill="none" 
              stroke={isDark ? "#00f5d4" : "#06b6d4"} 
              strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <div 
            className="absolute inset-0 rounded-full animate-ping opacity-10" 
            style={{ 
              background: isDark ? "#00f5d4" : "#06b6d4", 
              animationDuration: "2s" 
            }} 
          />
        </div>
        <div>
          <div 
            className="font-display font-bold text-sm tracking-widest group-hover:text-plasma transition-colors" 
            style={{ 
              letterSpacing: "0.15em",
              color: isDark ? "white" : "#1f2937"
            }}
          >
            ASCLEPIUS
          </div>
          <div 
            className="font-mono text-xs tracking-widest" 
            style={{ 
              color: isDark ? "#00f5d4" : "#06b6d4", 
              opacity: 0.6, 
              fontSize: "9px" 
            }}
          >
            AI · ICU COMMAND
          </div>
        </div>
      </Link>

      {/* Nav Links */}
      <div className="flex items-center gap-1">
        {NAV_LINKS.map((link) => {
          const active = location.pathname === link.path;
          return (
            <Link key={link.path} to={link.path}>
              <motion.div
                whileHover={{ y: -1 }}
                className="relative px-4 py-2 rounded-lg font-mono text-xs tracking-widest transition-all"
                style={{
                  color: active 
                    ? (isDark ? "#00f5d4" : "#06b6d4") 
                    : (isDark ? "rgba(255,255,255,0.35)" : "rgba(55,65,81,0.6)"),
                  background: active 
                    ? (isDark ? "rgba(0,245,212,0.08)" : "rgba(6,182,212,0.1)") 
                    : "transparent",
                  border: active 
                    ? (isDark ? "1px solid rgba(0,245,212,0.2)" : "1px solid rgba(6,182,212,0.3)") 
                    : "1px solid transparent",
                }}
              >
                <span className="mr-1.5 opacity-60">{link.icon}</span>
                {link.label}
                {active && (
                  <motion.div
                    layoutId="navIndicator"
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full"
                    style={{ 
                      background: isDark ? "#00f5d4" : "#06b6d4", 
                      boxShadow: isDark ? "0 0 8px #00f5d4" : "0 0 8px #06b6d4" 
                    }}
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </div>

      {/* Right side: theme toggle + clock + status */}
      <div className="flex items-center gap-4">
        {/* Theme toggle */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
          style={{
            background: isDark 
              ? "rgba(255,255,255,0.05)" 
              : "rgba(55,65,81,0.08)",
            border: isDark 
              ? "1px solid rgba(255,255,255,0.1)" 
              : "1px solid rgba(55,65,81,0.15)",
          }}
        >
          <span className="text-xs opacity-60">{isDark ? "🌙" : "☀️"}</span>
        </motion.button>

        {/* Live clock */}
        <div 
          className="font-mono text-xs tabular-nums" 
          style={{ 
            color: isDark 
              ? "rgba(255,255,255,0.3)" 
              : "rgba(55,65,81,0.5)" 
          }}
        >
          <span style={{ 
            color: isDark 
              ? "rgba(0,245,212,0.7)" 
              : "rgba(6,182,212,0.8)" 
          }}>{hh}:{mm}</span>
          <span className="opacity-50">:{ss}</span>
          <span className="ml-1 opacity-30">IST</span>
        </div>

        {/* Connection dot */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <div
              className="w-2 h-2 rounded-full"
              style={{ background: connected ? "#39ff14" : "#ff2d78" }}
            />
            {connected && (
              <div
                className="absolute inset-0 rounded-full animate-ping"
                style={{ background: "#39ff14", animationDuration: "2s" }}
              />
            )}
          </div>
          <span 
            className="font-mono text-xs" 
            style={{ 
              color: connected ? "#39ff14" : "#ff2d78", 
              opacity: 0.7 
            }}
          >
            {connected ? "LIVE" : "OFFLINE"}
          </span>
        </div>
      </div>
    </motion.nav>
  );
}
