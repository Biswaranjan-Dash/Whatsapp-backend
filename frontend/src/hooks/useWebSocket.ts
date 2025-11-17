import { useEffect, useState, useCallback, useRef } from "react";
import type { QueueSnapshot, WebSocketMessage, ConnectionStatus } from "@/types/appointment";

interface UseWebSocketOptions {
  url: string;
  date: string;
  onSnapshot?: (data: QueueSnapshot) => void;
  onUpdate?: (data: QueueSnapshot) => void;
  onError?: (error: string) => void;
}

export function useWebSocket({ url, date, onSnapshot, onUpdate, onError }: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [data, setData] = useState<QueueSnapshot | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const baseDelay = 1000;

  // Store callbacks in refs to avoid dependency issues
  const onSnapshotRef = useRef(onSnapshot);
  const onUpdateRef = useRef(onUpdate);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    onSnapshotRef.current = onSnapshot;
    onUpdateRef.current = onUpdate;
    onErrorRef.current = onError;
  }, [onSnapshot, onUpdate, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setStatus("connected");
      reconnectAttemptsRef.current = 0;

      // Subscribe to the date
      ws.send(
        JSON.stringify({
          action: "subscribe",
          date: date,
        })
      );
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        if (message.type === "snapshot" && message.data) {
          setData(message.data);
          onSnapshotRef.current?.(message.data);
        } else if (message.type === "update" && message.data) {
          setData(message.data);
          onUpdateRef.current?.(message.data);
        } else if (message.type === "error") {
          console.error("WebSocket error:", message.error);
          onErrorRef.current?.(message.error || "Unknown error");
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setStatus("error");
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setStatus("disconnected");
      wsRef.current = null;

      // Attempt to reconnect with exponential backoff
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = baseDelay * Math.pow(2, reconnectAttemptsRef.current);
        console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      } else {
        console.error("Max reconnection attempts reached");
        setStatus("error");
      }
    };
  }, [url, date]);

  const resubscribe = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("Resubscribing to date:", date);
      wsRef.current.send(
        JSON.stringify({
          action: "subscribe",
          date: date,
        })
      );
    }
  }, [date]);

  const retry = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    disconnect();
    connect();
  }, [connect, disconnect]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [url]); // Only reconnect when url changes

  // Handle date changes separately - resubscribe if already connected
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      resubscribe();
    }
  }, [date, resubscribe]);

  return { status, data, retry };
}
