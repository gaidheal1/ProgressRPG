import { useState, useRef, useEffect, useCallback } from 'react';
import { apiFetch } from '../../utils/api';

export function useWebSocketConnection(
  playerId,
  onMessage,
  onError,
  onClose,
  onOpen
) {
  const socketRef = useRef(null);
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);

  const [isConnected, setIsConnected] = useState(false);

  const maxReconnectAttempts = 10;
  const baseReconnectInterval = 1000; // 1 second
  const reconnectDecay = 1.5;

  const connectWebSocket = useCallback(async () => {
    if (!playerId) return;

    try {
      const { uuid } = await apiFetch('/ws_auth/');

      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const url = new URL(baseUrl);
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${url.hostname}:${url.port}/ws/profile_${playerId}/?uuid=${uuid}`;

      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
        socket.send(JSON.stringify({ type: 'ping' }));

        onOpen?.();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (e) {
          console.error('[WS] JSON parse error:', e);
        }
      };

      socket.onerror = (err) => {
        console.error('[WS] Error:', err);
        onError?.(err);
      };

      socket.onclose = () => {
        setIsConnected(false);
        onClose?.();

        if (reconnectAttempts.current < maxReconnectAttempts) {
          const timeout = baseReconnectInterval * (reconnectDecay ** reconnectAttempts.current);
          reconnectAttempts.current += 1;

          reconnectTimeout.current = setTimeout(() => {
            connectWebSocket();
          }, timeout);
        } else {
          console.warn('[WS] Max reconnect attempts reached, giving up');
        }
      };
    } catch (err) {
      console.error('[WS] Failed to authenticate or connect:', err);
      onError?.(err);

      if (reconnectAttempts.current < maxReconnectAttempts) {
        const timeout = baseReconnectInterval * (reconnectDecay ** reconnectAttempts.current);
        reconnectAttempts.current += 1;

        reconnectTimeout.current = setTimeout(() => {
          connectWebSocket();
        }, timeout);
      }
    }
  }, [playerId, onMessage, onError, onClose, onOpen]);

  useEffect(() => {
    if (!playerId) return;

    connectWebSocket();

    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [playerId, connectWebSocket]);

  const send = useCallback((payload) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    } else {
      console.warn('[WS] Socket not open');
    }
  }, []);

  return { send, isConnected };
}
