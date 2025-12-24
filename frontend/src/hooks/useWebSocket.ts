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
  const [isInitializing, setIsInitializing] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isInitialMount = useRef(true);
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
    // Skip if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    try {
      setStatus("connecting");
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isInitialMount.current) {
          isInitialMount.current = false;
        }
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
            setIsInitializing(false); // Mark initialization complete on first snapshot
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

      ws.onerror = () => {
        // WebSocket error events don't contain useful error info
        // The actual error details will be in the onclose event
        setStatus("error");
        setIsInitializing(false); // Stop initializing on error
      };

      ws.onclose = (event) => {
        const wasClean = event.wasClean;
        const code = event.code;
        const reason = event.reason || "Connection closed";
        
        if (!wasClean) {
          console.warn(`WebSocket closed unexpectedly: ${code} - ${reason}`);
        }
        
        setStatus("disconnected");
        wsRef.current = null;

        // Don't reconnect if this is an intentional close (code 1000)
        if (code === 1000) {
          return;
        }

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
          setIsInitializing(false);
          onErrorRef.current?.("Failed to connect to WebSocket after multiple attempts");
        }
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      setStatus("error");
      setIsInitializing(false);
      onErrorRef.current?.("Failed to initialize WebSocket connection");
    }
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
    setIsInitializing(true);
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

  return { status, data, isInitializing, retry };
}
