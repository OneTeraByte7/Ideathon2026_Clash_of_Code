import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

export default function LandingPage() {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem("asclepius-theme") || "dark";
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  const applyTheme = (selectedTheme) => {
    document.body.className = selectedTheme === "light" ? "light" : "";
    localStorage.setItem("asclepius-theme", selectedTheme);
  };

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  const isDark = theme === "dark";

  return (
    <div className={`min-h-screen transition-all duration-500 ${
      isDark 
        ? "bg-gradient-to-br from-[#0a0e27] via-[#0d1235] to-[#1a2847]" 
        : "bg-gradient-to-br from-gray-50 via-white to-blue-50"
    }`}>
      
      {/* Theme Toggle */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
        onClick={toggleTheme}
        className={`fixed top-6 right-6 z-50 p-3 rounded-full transition-all ${
          isDark 
            ? "bg-[#1a3a4a] text-[#00f5d4] hover:bg-[#2a4a5a]" 
            : "bg-white text-blue-600 hover:bg-gray-50 shadow-lg"
        }`}
      >
        {isDark ? "☀️" : "🌙"}
      </motion.button>

      <div className="relative overflow-hidden">
        {/* Animated Background Elements */}
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className={`absolute top-20 left-20 w-96 h-96 rounded-full blur-3xl ${
            isDark ? "bg-[#00f5d4]" : "bg-blue-200"
          }`}
        />
        <motion.div
          animate={{
            x: [0, -80, 0],
            y: [0, 80, 0],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{ duration: 12, repeat: Infinity }}
          className={`absolute bottom-20 right-20 w-80 h-80 rounded-full blur-3xl ${
            isDark ? "bg-purple-500" : "bg-indigo-200"
          }`}
        />

        {/* Main Content */}
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
          
          {/* Logo and Title */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-12"
          >
            <div className="flex items-center justify-center mb-6">
              <div className="relative w-16 h-16 mr-4">
                <svg viewBox="0 0 64 64" className="w-16 h-16">
                  <circle cx="32" cy="32" r="28" fill="none" 
                    stroke={isDark ? "#00f5d4" : "#2563eb"} 
                    strokeWidth="2" opacity="0.3" />
                  <circle cx="32" cy="32" r="18" fill="none" 
                    stroke={isDark ? "#00f5d4" : "#2563eb"} 
                    strokeWidth="1.5" opacity="0.5" />
                  <motion.path 
                    d="M16 32 L26 32 L30 22 L34 42 L38 32 L48 32" 
                    fill="none" 
                    stroke={isDark ? "#00f5d4" : "#2563eb"} 
                    strokeWidth="2" 
                    strokeLinecap="round"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, delay: 0.5 }}
                  />
                </svg>
                <motion.div 
                  className={`absolute inset-0 rounded-full animate-ping opacity-20`}
                  style={{ background: isDark ? "#00f5d4" : "#2563eb" }}
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
              </div>
            </div>
            
            <h1 className={`text-6xl font-bold mb-4 tracking-tight ${
              isDark ? "text-white" : "text-gray-900"
            }`}>
              ASCLEPIUS
            </h1>
            
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
              className={`text-lg tracking-widest font-mono ${
                isDark ? "text-[#00f5d4]" : "text-blue-600"
              }`}
            >
              AI-POWERED ICU COMMAND SYSTEM
            </motion.div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2, duration: 0.8 }}
            className="grid md:grid-cols-3 gap-6 mb-12 max-w-4xl"
          >
            {[
              {
                icon: "🧠",
                title: "AI-Powered Analysis",
                desc: "Advanced machine learning for sepsis prediction and risk assessment"
              },
              {
                icon: "⚡",
                title: "Real-Time Monitoring",
                desc: "Continuous patient monitoring with instant alert generation"
              },
              {
                icon: "📱",
                title: "Smart Protocols",
                desc: "AI-generated treatment protocols with doctor approval workflow"
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 + i * 0.1 }}
                className={`p-6 rounded-xl border backdrop-blur-sm transition-all hover:scale-105 ${
                  isDark 
                    ? "bg-[#0a1429]/50 border-[#1a3a4a] hover:bg-[#0a1429]/70" 
                    : "bg-white/80 border-gray-200 hover:bg-white shadow-lg"
                }`}
              >
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h3 className={`font-bold mb-2 ${
                  isDark ? "text-white" : "text-gray-900"
                }`}>{feature.title}</h3>
                <p className={`text-sm ${
                  isDark ? "text-gray-300" : "text-gray-600"
                }`}>{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8, duration: 0.8 }}
            className="flex gap-4"
          >
            <Link to="/dashboard">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all ${
                  isDark 
                    ? "bg-[#00f5d4] text-[#0a0e27] hover:bg-[#00e6c3] shadow-lg shadow-[#00f5d4]/25" 
                    : "bg-blue-600 text-white hover:bg-blue-700 shadow-lg"
                }`}
              >
                Enter ICU Dashboard
              </motion.button>
            </Link>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-8 py-4 rounded-xl font-semibold text-lg border transition-all ${
                isDark 
                  ? "border-[#00f5d4] text-[#00f5d4] hover:bg-[#00f5d4]/10" 
                  : "border-blue-600 text-blue-600 hover:bg-blue-50"
              }`}
            >
              Learn More
            </motion.button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.2 }}
            className={`mt-16 grid grid-cols-3 gap-8 text-center ${
              isDark ? "text-gray-300" : "text-gray-600"
            }`}
          >
            <div>
              <div className={`text-2xl font-bold ${
                isDark ? "text-[#00f5d4]" : "text-blue-600"
              }`}>99.7%</div>
              <div className="text-sm">Accuracy</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${
                isDark ? "text-[#00f5d4]" : "text-blue-600"
              }`}>24/7</div>
              <div className="text-sm">Monitoring</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${
                isDark ? "text-[#00f5d4]" : "text-blue-600"
              }`}>&lt;30s</div>
              <div className="text-sm">Response Time</div>
            </div>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.5 }}
          className={`absolute bottom-4 left-4 text-xs ${
            isDark ? "text-gray-500" : "text-gray-400"
          }`}
        >
          © 2026 Asclepius AI • Powered by Advanced ML
        </motion.footer>
      </div>
    </div>
  );
}