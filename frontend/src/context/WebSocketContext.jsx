// context/WebSocketContext.jsx
import React, { createContext, useContext, useRef, useCallback } from 'react';
import { useGame } from './GameContext';
import { useToast } from './ToastContext';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
import { handleGlobalWebSocketEvent } from '../websockets/handleGlobalWebSocketEvent';

const WebSocketContext = createContext();

export function WebSocketProvider({ children }) {
  const { player } = useGame();
  const { showToast } = useToast();
  const eventHandlersRef = useRef(new Set());

  const onMessage = useCallback((data) => {
    //console.log("[WS Provider] showToast:", showToast);
    handleGlobalWebSocketEvent(data, { showToast });

    eventHandlersRef.current.forEach((handler) => handler(data));
  }, [showToast]);

  const onError = useCallback(() => {
    console.error('WebSocket connection error');
  }, []);

  const onClose = useCallback(() => {
    console.warn('WebSocket disconnected');
  }, []);

  const onOpen = useCallback(() => {
    //console.log('WebSocket connected!');
  }, []);

  const { send, isConnected } = useWebSocketConnection(
    player?.id,
    onMessage,
    onError,
    onClose,
    onOpen
  );

  const addEventHandler = useCallback((handler) => {
    eventHandlersRef.current.add(handler);
    return () => eventHandlersRef.current.delete(handler);
  }, []);


  return (
    <WebSocketContext.Provider value={{ send, isConnected, addEventHandler }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  return useContext(WebSocketContext);
}
