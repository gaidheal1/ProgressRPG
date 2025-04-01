import { initialiseApp } from './init/appInit.js';
import { setupGlobalErrorHandlers } from './handlers/globalErrorHandlers.js';

document.addEventListener("DOMContentLoaded", () => {
  setupGlobalErrorHandlers();
  initialiseApp();
});
