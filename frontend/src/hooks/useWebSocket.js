import { useEffect, useRef, useState } from "react";

export function useWebSocket(path = "/ws/updates") {
  const WS_BASE = import.meta.env.VITE_WS_BASE || "ws://localhost:8000";
  const [isOpen, setIsOpen] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const url = `${WS_BASE}${path}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setIsOpen(true);
    ws.onclose = () => setIsOpen(false);
    ws.onerror = () => setIsOpen(false);
    ws.onmessage = (evt) => {
      try {
        setLastMessage(JSON.parse(evt.data));
      } catch {
        // ignore
      }
    };

    return () => {
      try { ws.close(); } catch {}
    };
  }, [WS_BASE, path]);

  return { isOpen, lastMessage };
}
