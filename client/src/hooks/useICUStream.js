import { useEffect, useRef, useState, useCallback } from "react";
import { createWS } from "../lib/api";

export function useICUStream() {
  const [snapshot, setSnapshot] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const ws = createWS();
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onmessage = (e) => {
        try { setSnapshot(JSON.parse(e.data)); } catch {}
      };
      ws.onclose = () => {
        setConnected(false);
        retryRef.current = setTimeout(() => {
          wsRef.current?.close();
          connect();
        }, 3000);
      };
      ws.onerror = () => ws.close();
    } catch {
      retryRef.current = setTimeout(() => connect(), 3000);
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
