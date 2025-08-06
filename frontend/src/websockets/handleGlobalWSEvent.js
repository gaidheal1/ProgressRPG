// websockets/handleGlobalWebSocketEvent.js
import { useToasts } from '../hooks/useToasts';

export default function handleGlobalWebSocketEvent(data, { showToast }) {
  if (data.type === 'notification') {
    showToast?.(data.message);
  }

  if (data.type === 'console.log') {
    console.log('[WS]', data.message);
  }

  if (data.type === 'pong') {
    console.log('[WS] Pong!');
  }
}
