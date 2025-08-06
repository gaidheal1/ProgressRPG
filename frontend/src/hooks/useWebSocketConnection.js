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
  const connectingRef = useRef(false);

  const maxReconnectAttempts = 10;
  const baseReconnectInterval = 1000; // 1 second
  const reconnectDecay = 1.5;

  const connectWebSocket = useCallback(async () => {
    if (connectingRef.current) {
      //console.log('[WS] Already connecting, skipping');
      return;
    }

    if (!playerId) return;

    connectingRef.current = true;

    if (socketRef.current) {
      if (
      socketRef.current.readyState === WebSocket.OPEN ||
      socketRef.current.readyState === WebSocket.CONNECTING
      ) {
        //console.log('[WS] Socket already open or connecting, skipping new connection');
       return;
      }
      // Only close if socket is OPEN or CONNECTING
      if (
        socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING
      ) {
        socketRef.current.close();
        socketRef.current = null;
      }
    }

    // Add small delay before actually connecting
    await new Promise((r) => setTimeout(r, 100));

    try {
      const { uuid } = await apiFetch('/ws_auth/');

      const baseUrl = import.meta.env.VITE_API_BASE_URL;
      const url = new URL(baseUrl);
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${url.hostname}:${url.port}/ws/profile_${playerId}/?uuid=${uuid}`;

      //console.log(`[WS] Attempting connection for player ${playerId}...`);
      //console.log('[WS] WebSocket URL:', wsUrl);

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        connectingRef.current = false;
        setIsConnected(true);
        reconnectAttempts.current = 0;

        onOpen?.();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (e) {
          //console.error('[WS] JSON parse error:', e);
        }
      };

      socket.onerror = (err) => {
        console.error('[WS] Error:', err);
        onError?.(err);
      };

      socket.onclose = (event) => {
        //console.log(`[WS] Socket closed. Code: ${event.code}, Reason: ${event.reason}, Clean: ${event.wasClean}`);
        connectingRef.current = false;
        setIsConnected(false);
        onClose?.();

        if (reconnectAttempts.current < maxReconnectAttempts) {
          const timeout = baseReconnectInterval * (reconnectDecay ** reconnectAttempts.current);
          reconnectAttempts.current += 1;
          //console.log(`[WS] Scheduling reconnect attempt ${reconnectAttempts.current} in ${timeout}ms`);
          reconnectTimeout.current = setTimeout(() => {
            connectWebSocket();
          }, timeout);
        } else {
          console.warn('[WS] Max reconnect attempts reached, giving up');
        }
      };
    } catch (err) {
      console.error('[WS] Failed to authenticate or connect:', err);
      connectingRef.current = false;
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
      //console.log('[WS] Effect cleanup: closing socket');
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
      if (socketRef.current) {
        //console.log('[WS] Closing socket', socketRef.current);
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
