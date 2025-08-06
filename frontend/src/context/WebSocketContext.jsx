// context/WebSocketContext.jsx
import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { useGame } from './GameContext';
import { useToasts } from '../hooks/useToasts';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';

const WebSocketContext = createContext();

export function WebSocketProvider({ children }) {
  const { player } = useGame();
  const { showToast } = useToasts();
  const eventHandlersRef = useRef(new Set());

 // Memoize event handlers to keep stable references and fresh closures
  const onMessage = useCallback((data) => {
    if (data.type === 'notification' && data.message) {
      showToast(data.message);
    }
    eventHandlersRef.current.forEach((handler) => handler(data));
  }, [showToast]);

  const onError = useCallback(() => {
    showToast('WebSocket connection error');
  }, [showToast]);

  const onClose = useCallback(() => {
    showToast('WebSocket disconnected');
  }, [showToast]);

  const onOpen = useCallback(() => {
    showToast('WebSocket connected!');
  }, [showToast]);

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
