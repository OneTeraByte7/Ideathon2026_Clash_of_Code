/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ["'Syne'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
        body: ["'DM Sans'", "sans-serif"],
      },
      colors: {
        void: "#03050a",
        obsidian: "#080c14",
        surface: "#0d1220",
        panel: "#111827",
        border: "#1a2540",
        plasma: "#00f5d4",
        pulse: "#ff2d78",
        warn: "#f59e0b",
        bio: "#39ff14",
        ice: "#38bdf8",
        ghost: "rgba(255,255,255,0.06)",
        
        // Light theme colors (softer versions)
        light: {
          bg: "#f8fafb",
          surface: "#ffffff",
          panel: "#f3f4f6",
          border: "#e5e7eb",
          text: "#374151",
          plasma: "#06b6d4",
          pulse: "#ec4899",
          warn: "#eab308",
          bio: "#84cc16",
          ice: "#0ea5e9",
        }
      },
      screens: {
        'xs': '320px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      }
    },
  },
  plugins: [],
};
