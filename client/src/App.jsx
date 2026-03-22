import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "./components/Navbar";
import SplashScreen from "./components/SplashScreen";
import { ToastProvider } from "./components/Toast";
import LandingPage from "./pages/LandingPage";
import LandingPageNew from "./pages/LandingPageNew";
import Dashboard from "./pages/Dashboard";
import AlertsPage from "./pages/AlertsPage";
import ProtocolsPage from "./pages/ProtocolsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import { useICUStream } from "./hooks/useICUStream";

function PageTransition({ children }) {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.25, ease: "easeInOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

function AppInner() {
  const { connected } = useICUStream();
  const location = useLocation();
  const isLanding = location.pathname === "/" || location.pathname === "/landing";
  
  return (
    <>
      {!isLanding && <Navbar connected={connected} />}
      <PageTransition>
        <Routes>
          <Route path="/"           element={<LandingPageNew />} />
          <Route path="/dashboard"  element={<Dashboard />} />
          <Route path="/landing"    element={<LandingPage />} />
          <Route path="/alerts"     element={<AlertsPage />} />
          <Route path="/protocols"  element={<ProtocolsPage />} />
          <Route path="/analytics"  element={<AnalyticsPage />} />
        </Routes>
      </PageTransition>
    </>
  );
}

export default function App() {
  const [booted, setBooted] = useState(false);

  useEffect(() => {
    // Apply theme on app start
    const savedTheme = localStorage.getItem("asclepius-theme") || "dark";
    document.body.className = savedTheme === "light" ? "light" : "";
  }, []);

  return (
    <ToastProvider>
      <BrowserRouter>
        {!booted && <SplashScreen onComplete={() => setBooted(true)} />}
        {booted && <AppInner />}
      </BrowserRouter>
    </ToastProvider>
  );
}
