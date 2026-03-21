import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_LINKS = [
  { path: "/",         label: "ICU GRID",   icon: "⬡" },
  { path: "/alerts",   label: "ALERTS",     icon: "◈" },
  { path: "/protocols",label: "PROTOCOLS",  icon: "⊕" },
  { path: "/analytics",label: "ANALYTICS",  icon: "≋" },
];

export default function Navbar({ connected }) {
  const location = useLocation();
  const [time, setTime] = useState(new Date());
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light');
    } else {
      document.body.classList.remove('light');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const hh = time.getHours().toString().padStart(2, "0");
  const mm = time.getMinutes().toString().padStart(2, "0");
  const ss = time.getSeconds().toString().padStart(2, "0");

  const isDark = theme === 'dark';
  const bgStyle = isDark 
    ? { background: "rgba(8,12,20,0.88)", borderBottom: "1px solid rgba(0,245,212,0.1)" }
    : { background: "rgba(248,250,251,0.92)", borderBottom: "1px solid rgba(6,182,212,0.15)" };

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 sm:px-8 py-4"
      style={{
        ...bgStyle,
        backdropFilter: "blur(24px)",
      }}
    >
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 sm:gap-3 group hover:opacity-80 transition-opacity flex-shrink-0">
        <img src="/logo.png" alt="Asclepius" className="w-8 sm:w-9 h-8 sm:h-9 object-contain" />
        <div className="hidden sm:block">
          <div className={`font-display font-bold text-sm sm:text-base tracking-widest group-hover:text-plasma transition-colors ${isDark ? 'text-white' : 'text-gray-900'}`}>
            ASCLEPIUS
          </div>
          <div className="font-mono text-xs tracking-widest" style={{ color: isDark ? "#00f5d4" : "#06b6d4", opacity: 0.7, fontSize: "9px" }}>
            AI · ICU
          </div>
        </div>
      </Link>

      {/* Mobile menu button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="sm:hidden flex flex-col gap-1.5 p-2"
        style={{ color: isDark ? "#00f5d4" : "#06b6d4" }}
      >
        <div className="w-5 h-0.5 transition-transform" style={{ background: isDark ? "rgba(0,245,212,0.6)" : "rgba(6,182,212,0.6)", transform: mobileMenuOpen ? 'rotate(45deg) translateY(8px)' : 'rotate(0)' }} />
        <div className="w-5 h-0.5" style={{ background: isDark ? "rgba(0,245,212,0.6)" : "rgba(6,182,212,0.6)", opacity: mobileMenuOpen ? 0 : 1 }} />
        <div className="w-5 h-0.5 transition-transform" style={{ background: isDark ? "rgba(0,245,212,0.6)" : "rgba(6,182,212,0.6)", transform: mobileMenuOpen ? 'rotate(-45deg) translateY(-8px)' : 'rotate(0)' }} />
      </button>

      {/* Desktop Nav Links */}
      <div className="hidden sm:flex items-center gap-1.5">
        {NAV_LINKS.map((link) => {
          const active = location.pathname === link.path;
          return (
            <Link key={link.path} to={link.path}>
              <motion.div
                whileHover={{ y: -2 }}
                className="relative px-4 sm:px-5 py-2 sm:py-2.5 rounded-lg font-mono text-xs tracking-widest transition-all hover:shadow-md"
                style={{
                  color: active ? (isDark ? "#00f5d4" : "#06b6d4") : (isDark ? "rgba(255,255,255,0.4)" : "rgba(55,65,81,0.4)"),
                  background: active ? (isDark ? "rgba(0,245,212,0.12)" : "rgba(6,182,212,0.12)") : "transparent",
                  border: active ? (isDark ? "1px solid rgba(0,245,212,0.25)" : "1px solid rgba(6,182,212,0.25)") : "1px solid transparent",
                }}
              >
                <span className="mr-1.5 sm:mr-2 opacity-70">{link.icon}</span>
                <span className="hidden md:inline">{link.label}</span>
                {active && (
                  <motion.div
                    layoutId="navIndicator"
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full"
                    style={{ background: isDark ? "#00f5d4" : "#06b6d4", boxShadow: `0 0 12px ${isDark ? '#00f5d4' : '#06b6d4'}` }}
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </div>

      {/* Right side: clock + theme + status */}
      <div className="hidden sm:flex items-center gap-3 sm:gap-5">
        {/* Live clock */}
        <div className="font-mono text-xs tabular-nums hidden md:block" style={{ color: isDark ? "rgba(255,255,255,0.35)" : "rgba(55,65,81,0.5)" }}>
          <span style={{ color: isDark ? "rgba(0,245,212,0.8)" : "rgba(6,182,212,0.8)" }} className="font-semibold">{hh}:{mm}</span>
          <span className="opacity-60">:{ss}</span>
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2.5 rounded-lg transition-all hover:shadow-md"
          style={{
            background: isDark ? "rgba(0,245,212,0.08)" : "rgba(6,182,212,0.08)",
            color: isDark ? "#00f5d4" : "#06b6d4",
            border: isDark ? "1px solid rgba(0,245,212,0.15)" : "1px solid rgba(6,182,212,0.15)",
          }}
          title={`Switch to ${isDark ? 'Light' : 'Dark'} mode`}
        >
          {isDark ? '☀️' : '🌙'}
        </button>

        {/* Connection dot */}
        <div className="flex items-center gap-2.5 px-3 sm:px-4 py-1.5 rounded-lg" style={{ background: connected ? (isDark ? "rgba(57,255,20,0.08)" : "rgba(132,204,22,0.08)") : (isDark ? "rgba(255,45,120,0.08)" : "rgba(236,72,153,0.08)") }}>
          <div className="relative">
            <div
              className="w-2 sm:w-2.5 h-2 sm:h-2.5 rounded-full"
              style={{ background: connected ? (isDark ? "#39ff14" : "#84cc16") : (isDark ? "#ff2d78" : "#ec4899") }}
            />
            {connected && (
              <div
                className="absolute inset-0 rounded-full animate-ping"
                style={{ background: connected ? (isDark ? "#39ff14" : "#84cc16") : (isDark ? "#ff2d78" : "#ec4899"), animationDuration: "2s" }}
              />
            )}
          </div>
          <span className="font-mono text-xs font-semibold hidden sm:inline" style={{ color: connected ? (isDark ? "#39ff14" : "#84cc16") : (isDark ? "#ff2d78" : "#ec4899"), opacity: 0.85 }}>
            {connected ? "LIVE" : "OFFLINE"}
          </span>
        </div>
      </div>

      {/* Mobile theme toggle */}
      <button
        onClick={toggleTheme}
        className="sm:hidden p-2"
        style={{ color: isDark ? "#00f5d4" : "#06b6d4" }}
        title={`Switch to ${isDark ? 'Light' : 'Dark'} mode`}
      >
        {isDark ? '☀️' : '🌙'}
      </button>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-full left-0 right-0 mt-2 mx-4 rounded-lg p-4 flex flex-col gap-2"
          style={{
            background: isDark ? "rgba(8,12,20,0.95)" : "rgba(248,250,251,0.95)",
            border: isDark ? "1px solid rgba(0,245,212,0.15)" : "1px solid rgba(6,182,212,0.15)",
            backdropFilter: "blur(24px)",
          }}
        >
          {NAV_LINKS.map((link) => {
            const active = location.pathname === link.path;
            return (
              <Link key={link.path} to={link.path} onClick={() => setMobileMenuOpen(false)}>
                <div
                  className="px-4 py-2.5 rounded-lg transition-all"
                  style={{
                    color: active ? (isDark ? "#00f5d4" : "#06b6d4") : (isDark ? "rgba(255,255,255,0.6)" : "rgba(55,65,81,0.6)"),
                    background: active ? (isDark ? "rgba(0,245,212,0.1)" : "rgba(6,182,212,0.1)") : "transparent",
                  }}
                >
                  <span className="mr-2">{link.icon}</span>
                  {link.label}
                </div>
              </Link>
            );
          })}
        </motion.div>
      )}
    </motion.nav>
  );
}
