import { useEffect, useRef, useState, useCallback } from "react";
import { createWS } from "../lib/api";

export function useICUStream() {
  const [snapshot, setSnapshot] = useState(null);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const retryCount = useRef(0);
  const connectRef = useRef(null);

  const MAX_RETRIES = 3;

  const cleanup = () => {
    if (retryRef.current) {
      clearTimeout(retryRef.current);
      retryRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const connect = useCallback(() => {
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
        console.log("WebSocket connected");
        setConnected(true);
        retryCount.current = 0;
      };

      ws.onmessage = (e) => {
        try {
          setSnapshot(JSON.parse(e.data));
        } catch (err) {
          console.warn("Invalid WS message:", err);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
        setConnected(false);

        if (retryCount.current < MAX_RETRIES) {
          const delay = 2000 * Math.pow(2, retryCount.current);
          retryCount.current++;

          retryRef.current = setTimeout(() => {
            console.log(
              `Retry ${retryCount.current}/${MAX_RETRIES} in ${delay}ms`
            );
            connectRef.current?.(); // ✅ safe call
          }, delay);
        } else {
          console.log("Max retries reached");
        }
      };

      ws.onerror = (err) => {
        console.warn("WebSocket error:", err);
        ws.close();
      };

    } catch (err) {
      console.warn("Connection failed:", err);
      setConnected(false);
    }
  }, []);

  // ✅ Update ref AFTER render
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // ✅ Initial connect
  useEffect(() => {
    connectRef.current?.();

    return () => {
      cleanup();
    };
  }, []);

  return { snapshot, connected };
}