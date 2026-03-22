import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { useState } from "react";

export default function LandingPage() {
  const [isDark, setIsDark] = useState(true);

  const theme = isDark ? {
    bg: "linear-gradient(135deg, #0a0f1c, #1a1f2e)",
    cardBg: "rgba(13,18,32,0.8)",
    text: "#ffffff",
    accent: "#00f5d4",
    secondary: "rgba(255,255,255,0.7)",
    border: "rgba(0,245,212,0.2)"
  } : {
    bg: "linear-gradient(135deg, #f8fafc, #e2e8f0)",
    cardBg: "rgba(255,255,255,0.9)",
    text: "#1e293b",
    accent: "#0ea5e9",
    secondary: "rgba(30,41,59,0.7)",
    border: "rgba(14,165,233,0.2)"
  };

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{ background: theme.bg }}
    >
      {/* Background patterns */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-72 h-72 rounded-full blur-3xl" 
             style={{ background: theme.accent }} />
        <div className="absolute bottom-20 right-20 w-96 h-96 rounded-full blur-3xl" 
             style={{ background: theme.accent }} />
      </div>

      {/* Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 flex items-center justify-between p-6"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8">
            <svg viewBox="0 0 32 32" className="w-8 h-8">
              <circle cx="16" cy="16" r="14" fill="none" stroke={theme.accent} strokeWidth="1.5" opacity="0.4" />
              <circle cx="16" cy="16" r="9" fill="none" stroke={theme.accent} strokeWidth="1" opacity="0.6" />
              <path d="M8 16 L13 16 L15 11 L17 21 L19 16 L24 16" fill="none" stroke={theme.accent} strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h1 className="font-display font-bold text-xl tracking-widest" style={{ color: theme.text }}>
              ASCLEPIUS
            </h1>
            <p className="font-mono text-xs tracking-widest opacity-60" style={{ color: theme.accent }}>
              AI · ICU COMMAND
            </p>
          </div>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setIsDark(!isDark)}
          className="p-2 rounded-lg transition-all"
          style={{ 
            background: theme.cardBg, 
            border: `1px solid ${theme.border}`,
            color: theme.text
          }}
        >
          {isDark ? "☀️" : "🌙"}
        </button>
      </motion.header>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20">
        
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-16"
        >
          <h2 className="font-display font-bold text-5xl mb-6 leading-tight" style={{ color: theme.text }}>
            AI-Powered ICU
            <span className="block" style={{ color: theme.accent }}>
              Sepsis Detection
            </span>
          </h2>
          <p className="font-mono text-lg max-w-2xl mx-auto leading-relaxed" style={{ color: theme.secondary }}>
            Advanced machine learning algorithms monitor patient vitals in real-time, 
            detecting early signs of sepsis to save lives through rapid intervention.
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {[
            {
              icon: "🏥",
              title: "Real-time Monitoring",
              description: "Continuous vital sign analysis with instant anomaly detection"
            },
            {
              icon: "🤖",
              title: "AI Predictions",
              description: "Machine learning models trained on medical data for early warnings"
            },
            {
              icon: "📱",
              title: "Instant Alerts",
              description: "Telegram notifications to medical staff for immediate response"
            }
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="rounded-2xl p-8 backdrop-blur-lg transition-all hover:scale-105"
              style={{ 
                background: theme.cardBg,
                border: `1px solid ${theme.border}`,
                boxShadow: isDark ? "0 20px 60px rgba(0,0,0,0.3)" : "0 20px 60px rgba(0,0,0,0.1)"
              }}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="font-display font-bold text-xl mb-3" style={{ color: theme.text }}>
                {feature.title}
              </h3>
              <p className="font-mono text-sm leading-relaxed" style={{ color: theme.secondary }}>
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center"
        >
          <Link to="/dashboard">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-12 py-4 rounded-2xl font-display font-bold text-lg tracking-wider transition-all shadow-2xl"
              style={{ 
                background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}dd)`,
                color: isDark ? "#ffffff" : "#ffffff",
                boxShadow: `0 20px 60px ${theme.accent}30`
              }}
            >
              ENTER ICU DASHBOARD →
            </motion.button>
          </Link>
          
          <p className="font-mono text-xs mt-4 opacity-60 tracking-widest" style={{ color: theme.secondary }}>
            MEDICAL GRADE • REAL-TIME • AI-POWERED
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-20 grid grid-cols-3 gap-8 text-center"
        >
          {[
            { value: "99.2%", label: "ACCURACY" },
            { value: "<3s", label: "RESPONSE TIME" },
            { value: "24/7", label: "MONITORING" }
          ].map((stat, index) => (
            <div key={stat.label}>
              <div className="font-display font-bold text-3xl mb-2" style={{ color: theme.accent }}>
                {stat.value}
              </div>
              <div className="font-mono text-xs tracking-widest opacity-60" style={{ color: theme.text }}>
                {stat.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="relative z-10 text-center py-8 border-t"
        style={{ borderColor: theme.border }}
      >
        <p className="font-mono text-xs opacity-40 tracking-widest" style={{ color: theme.text }}>
          © 2026 ASCLEPIUS AI • ICU SEPSIS EARLY WARNING SYSTEM
        </p>
      </motion.footer>
    </div>
  );
}