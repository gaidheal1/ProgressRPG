import { submitBugReport } from '../modules/bugReporter.js';

export function setupGlobalErrorHandlers() {
  window.onerror = function (message, source, lineno, colno, error) {
    console.error("Global error captured:", { message, source, lineno, colno, error });
    submitBugReport({ message, source, lineno, colno, error });
  };

  window.onunhandledrejection = function (event) {
    console.error("Unhandled promise rejection:", event.reason);
    submitBugReport({ message: "Unhandled promise rejection", error: event.reason });
  };
}
