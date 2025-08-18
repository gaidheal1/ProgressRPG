// websockets/handleGlobalWebSocketEvent.js

export function handleGlobalWebSocketEvent(data, { showToast, maintenanceRefetch }) {
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

    case 'action':
      switch (data.action) {
        case 'refresh':
          if (maintenanceRefetch) {
            maintenanceRefetch();
          } else {
            console.warn('[WS] maintenanceRefetch not provided, cannot refresh.');
          }
          break;
        default:
          console.warn('[WS] Unknown action:', data);
      }

    default:
      console.warn('[WS] Unknown type:', data);
  }
}
