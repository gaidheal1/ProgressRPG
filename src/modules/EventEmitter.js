export class EventEmitter {
  constructor() {
    this.events = {};
  }

  // Subscribe to an event
  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }

  // Unsubscribe
  off(event, listener) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter((l) => l !== listener);
  }

  // Emit
  emit(event, data) {
    if (!this.events[event]) return;
    this.events[event].forEach((listener) => listener(data));
  }
}