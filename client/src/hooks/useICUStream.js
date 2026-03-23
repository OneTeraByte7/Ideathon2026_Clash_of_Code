import { useEffect, useRef, useState, useCallback } from "react";
import { createWS } from "../lib/api";

export function useICUStream() {
  const [snapshot, setSnapshot] = useState(null);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const retryCount = useRef(0);
  const connectRef = useRef(null);
  const mountedRef = useRef(true);

  const MAX_RETRIES = 3;
  const RETRY_DELAYS = [2000, 5000, 10000]; // Progressive delays

  const cleanup = () => {
    if (retryRef.current) {
      clearTimeout(retryRef.current);
      retryRef.current = null;
    }

    if (wsRef.current) {
      // Remove event listeners before closing
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      
      if (wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, "Component unmounting");
      }
      wsRef.current = null;
    }
  };

  const connect = useCallback(() => {
    // Don't connect if component is unmounted
    if (!mountedRef.current) return;
    
    cleanup();

    try {
      const ws = createWS();

      if (!ws) {
        console.log("WebSocket unavailable, fallback mode");
        setConnected(false);
        return;
      }

      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;
        console.log("WebSocket connected");
        setConnected(true);
        retryCount.current = 0;
      };

      ws.onmessage = (e) => {
        if (!mountedRef.current) return;
        try {
          const data = JSON.parse(e.data);
          
          // Handle different message types
          if (data.type === "heartbeat") {
            // Just acknowledge heartbeat, don't update UI
            console.log("💓 Heartbeat received");
            return;
          }
          
          // Validate ICU snapshot data structure
          if (data && data.type === "icu_snapshot" && Array.isArray(data.patients)) {
            // Ensure each patient has a valid ID
            const validatedPatients = data.patients.map((p, index) => ({
              ...p,
              id: p.id || `patient-${index}-${p.name || 'unknown'}`
            }));
            
            setSnapshot({
              ...data,
              patients: validatedPatients
            });
          } else if (data.type === "error") {
            console.warn("Server error:", data.message);
          }
        } catch (err) {
          console.warn("Invalid WS message:", err);
        }
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;
        
        console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
        setConnected(false);

        // Only retry if it's an unexpected closure (not manual close)
        if (event.code !== 1000 && retryCount.current < MAX_RETRIES) {
          const delay = RETRY_DELAYS[retryCount.current] || 10000;
          retryCount.current++;

          console.log(`Retry ${retryCount.current}/${MAX_RETRIES} in ${delay}ms`);
          
          retryRef.current = setTimeout(() => {
            if (mountedRef.current && connectRef.current) {
              connectRef.current();
            }
          }, delay);
        } else if (retryCount.current >= MAX_RETRIES) {
          console.log("Max retries reached - WebSocket connection failed");
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket error:", err);
        // Don't close here - let onclose handle it
      };

    } catch (err) {
      console.warn("Connection failed:", err);
      setConnected(false);
    }
  }, []);

  // Update ref AFTER render
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Initial connect and cleanup
  useEffect(() => {
    mountedRef.current = true;
    
    // Add a small delay to prevent rapid connection attempts
    const initialDelay = setTimeout(() => {
      if (mountedRef.current && connectRef.current) {
        connectRef.current();
      }
    }, 100);

    return () => {
      mountedRef.current = false;
      clearTimeout(initialDelay);
      cleanup();
    };
  }, []);

  return { snapshot, connected };
}