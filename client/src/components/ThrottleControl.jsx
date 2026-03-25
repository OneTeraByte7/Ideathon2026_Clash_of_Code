import { useState, useEffect } from "react";
import { motion } from "framer-motion";

export default function ThrottleControl() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [newInterval, setNewInterval] = useState(15);
  const [status, setStatus] = useState(null);

  const loadConfig = async () => {
    try {
      const response = await fetch("/api/throttle/config");
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        setNewInterval(data.interval_seconds);
      }
    } catch (error) {
      console.error("Failed to load throttle config:", error);
      setStatus({ type: "error", message: "Failed to load configuration" });
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async () => {
    setUpdating(true);
    try {
      const response = await fetch("/api/throttle/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interval_seconds: newInterval,
          max_alerts_per_window: 1
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setStatus({ type: "success", message: result.message });
        await loadConfig();
      } else {
        setStatus({ type: "error", message: "Failed to update configuration" });
      }
    } catch (error) {
      console.error("Failed to update config:", error);
      setStatus({ type: "error", message: "Failed to update configuration" });
    } finally {
      setUpdating(false);
    }
  };

  const clearThrottles = async () => {
    try {
      const response = await fetch("/api/throttle/throttles", {
        method: "DELETE",
      });

      if (response.ok) {
        const result = await response.json();
        setStatus({ 
          type: "success", 
          message: `Cleared ${result.cleared_count} active throttles` 
        });
        await loadConfig();
      } else {
        setStatus({ type: "error", message: "Failed to clear throttles" });
      }
    } catch (error) {
      console.error("Failed to clear throttles:", error);
      setStatus({ type: "error", message: "Failed to clear throttles" });
    }
  };

  useEffect(() => {
    loadConfig();
    // Auto-refresh config every 30 seconds
    const interval = setInterval(loadConfig, 30000);
    return () => clearInterval(interval);
  }, []);

  // Clear status after 5 seconds
  useEffect(() => {
    if (status) {
      const timer = setTimeout(() => setStatus(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  if (loading) {
    return (
      <div className="rounded-2xl p-6" style={{ background: "#0d1220", border: "1px solid rgba(0,245,212,0.1)" }}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-700 rounded mb-3"></div>
          <div className="h-8 bg-gray-700 rounded mb-4"></div>
          <div className="h-4 bg-gray-700 rounded mb-2"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl p-6"
      style={{ 
        background: "#0d1220", 
        border: "1px solid rgba(0,245,212,0.2)",
        boxShadow: "0 0 20px rgba(0,245,212,0.05)"
      }}
    >
      <div className="flex items-center gap-3 mb-6">
        <span className="text-2xl">⏱️</span>
        <div>
          <h3 className="font-display font-bold text-xl text-white">Alert Throttling</h3>
          <p className="font-mono text-xs opacity-40 tracking-widest">
            PREVENT SPAM ALERTS · CONFIGURABLE INTERVALS
          </p>
        </div>
      </div>

      {/* Status Alert */}
      {status && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className={`rounded-xl p-3 mb-4 ${
            status.type === "error"
              ? "bg-red-500/10 border border-red-500/30 text-red-400"
              : "bg-green-500/10 border border-green-500/30 text-green-400"
          }`}
        >
          <div className="font-mono text-xs">
            {status.type === "error" ? "❌" : "✅"} {status.message}
          </div>
        </motion.div>
      )}

      {/* Current Configuration */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl p-4" style={{ background: "rgba(255,255,255,0.02)" }}>
          <div className="font-mono text-xs opacity-30 mb-1">CURRENT INTERVAL</div>
          <div className="font-display font-bold text-2xl" style={{ color: "#00f5d4" }}>
            {config?.interval_seconds}s
          </div>
        </div>
        <div className="rounded-xl p-4" style={{ background: "rgba(255,255,255,0.02)" }}>
          <div className="font-mono text-xs opacity-30 mb-1">ACTIVE THROTTLES</div>
          <div className="font-display font-bold text-2xl" style={{ color: "#f59e0b" }}>
            {config?.active_throttles || 0}
          </div>
        </div>
      </div>

      {/* Configuration Controls */}
      <div className="space-y-4">
        <div>
          <label className="block font-mono text-xs opacity-60 mb-2 tracking-widest">
            THROTTLE INTERVAL (SECONDS)
          </label>
          <div className="flex items-center gap-3">
            <input
              type="range"
              min="5"
              max="60"
              value={newInterval}
              onChange={(e) => setNewInterval(parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #00f5d4 0%, #00f5d4 ${((newInterval - 5) / 55) * 100}%, #374151 ${((newInterval - 5) / 55) * 100}%, #374151 100%)`
              }}
            />
            <div className="w-16 text-center">
              <span className="font-mono text-sm font-bold" style={{ color: "#00f5d4" }}>
                {newInterval}s
              </span>
            </div>
          </div>
          <div className="font-mono text-xs opacity-30 mt-1">
            Minimum time between alerts for the same patient
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-6">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={updateConfig}
            disabled={updating || newInterval === config?.interval_seconds}
            className="flex-1 py-3 px-4 rounded-xl font-mono text-xs tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: newInterval !== config?.interval_seconds 
                ? "rgba(0,245,212,0.15)" 
                : "rgba(255,255,255,0.05)",
              border: `1px solid ${newInterval !== config?.interval_seconds 
                ? "rgba(0,245,212,0.3)" 
                : "rgba(255,255,255,0.1)"}`,
              color: newInterval !== config?.interval_seconds 
                ? "#00f5d4" 
                : "rgba(255,255,255,0.4)"
            }}
          >
            {updating ? "UPDATING..." : "UPDATE CONFIG"}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={clearThrottles}
            className="py-3 px-4 rounded-xl font-mono text-xs tracking-widest transition-all"
            style={{
              background: "rgba(245,158,11,0.1)",
              border: "1px solid rgba(245,158,11,0.3)",
              color: "#f59e0b"
            }}
          >
            CLEAR ALL
          </motion.button>
        </div>
      </div>

      {/* Description */}
      <div className="mt-6 p-4 rounded-xl" style={{ background: "rgba(255,255,255,0.02)" }}>
        <div className="font-mono text-xs opacity-60 leading-relaxed">
          {config?.description || "Alert throttling prevents spam when critical buttons are pressed multiple times."}
        </div>
      </div>
    </motion.div>
  );
}