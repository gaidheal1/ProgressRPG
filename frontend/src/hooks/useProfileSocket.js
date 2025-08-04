// hooks/useProfileSocket.js
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;
import { useEffect, useRef } from 'react';
import { usePlayer } from '../context/PlayerContext';

export default function useProfileSocket(onEvent) {
  const { player } = usePlayer();
  //console.log("Player inside ws:", player);
  const url = new URL(rawBaseUrl);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!player || !player.id) {
      //console.log('WebSocket Waiting for player...');
      return;
    }

    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${url.hostname}:${url.port}/ws/profile_${player.id}/`);
    socketRef.current = socket;

    socket.onopen = () => {
      //console.log('[WS] Connected');
      socket.send(JSON.stringify({ type: 'ping' }));
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        //console.log('[WS] Received:', data);
        onEvent?.(data);
      } catch (e) {
        console.error('[WS] JSON parse error:', e);
      }
    };

    socket.onerror = (err) => {
      console.error('[WS] Error:', err);
    };

    socket.onclose = () => {
      console.warn('[WS] Closed');
    };

    return () => socket.close();
  }, [player?.id, onEvent]);

  const send = (payload) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    } else {
      console.warn('[WS] Socket not open');
    }
  };

  return { send };
}
