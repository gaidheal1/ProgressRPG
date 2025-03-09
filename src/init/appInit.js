import { initialiseTimers } from './timers.js';
import { setupEventListeners } from './eventListenerSetup.js';
import { updateUI } from '../handlers/uiHandlers.js';
import { connectWebsocket } from '../modules/WebSocketManager.js';

export function initialiseApp() {
  initialiseTimers();
  setupEventListeners();
  updateUI();
  connectWebsocket();
}
