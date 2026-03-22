import { useEffect, useRef, useState, useCallback } from "react";
import { createWS } from "../lib/api";

export function useICUStream() {
  const [snapshot, setSnapshot] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const maxRetries = useRef(3);
  const retryCount = useRef(0);

  const connect = useCallback(() => {
    try {
      const ws = createWS();
      
      // If WebSocket creation failed, don't retry excessively
      if (!ws) {
        console.log("WebSocket not available, using fallback mode");
        setConnected(false);
        return;
      }
      
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnected(true);
        retryCount.current = 0; // Reset retry count on successful connection
      };
      
      ws.onmessage = (e) => {
        try { 
          setSnapshot(JSON.parse(e.data)); 
        } catch (err) {
          console.warn("Failed to parse WebSocket message:", err);
        }
      };
      
      ws.onclose = () => {
        setConnected(false);
        console.log("WebSocket disconnected");
        
        // Only retry if we haven't exceeded max retries
        if (retryCount.current < maxRetries.current) {
          retryCount.current++;
          retryRef.current = setTimeout(() => {
            console.log(`WebSocket retry ${retryCount.current}/${maxRetries.current}`);
            connect();
          }, 5000); // Longer delay between retries
        } else {
          console.log("Max WebSocket retries reached, staying in offline mode");
        }
      };
      
      ws.onerror = (error) => {
        console.warn("WebSocket error:", error);
        ws.close();
      };
      
    } catch (error) {
      console.warn("WebSocket connection failed:", error);
      setConnected(false);
      
      // Only retry if we haven't exceeded max retries
      if (retryCount.current < maxRetries.current) {
        retryCount.current++;
        retryRef.current = setTimeout(() => connect(), 5000);
      }
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { snapshot, connected };
}
