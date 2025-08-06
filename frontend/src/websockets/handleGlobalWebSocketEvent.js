// websockets/handleGlobalWebSocketEvent.js

export function handleGlobalWebSocketEvent(data, { showToast }) {
  switch (data.type) {
    case 'notification':
      showToast?.(data.message);
      break;
    case 'console.log':
      console.log('[WS]', data.message);
      break;
    case 'pong':
      console.log('[WS] Pong!');
    break;
    default:
      console.warn('[WS] Unknown type:', data);
  }
}
