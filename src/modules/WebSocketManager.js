import { handleSocketMessage } from '../handlers/websocketHandlers.js';
import { handleReconnect } from '../handlers/reconnectHandlers.js';
import { pauseTimers } from '../handlers/timerHandlers.js'

export class ProfileWebSocket {
  constructor(profile_id) {
    this.profile_id = profile_id;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${protocol}://${window.location.host}/ws/profile_${this.profile_id}/`;
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log("Connected to timer socket");
        resolve();
        this.startPing();
        startTimers();
        this.reconnectAttempts = 0;
        handleReconnect();
      };

      this.socket.onmessage = (event) => {
        let data;
        try {
          data = JSON.parse(event.data);
          console.log("Received message:", data);
          handleSocketMessage(data);
        } catch (e) {
          console.error("Error parsing JSON:", e, event.data);
        }
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        reject(error);
      };

      this.socket.onclose = (event) => {
        console.log("Socket closed:", event);
        this.stopPing();
        pauseTimers();
        this.reconnect();
      };
    });
  }

  startTimers() {
    this.send({ action: "start_timers_request" });
  }

  pauseTimers() {
    console.log("WS attempting to pause timers...");
    this.send({ action: "pause_timers_request" });
  }

  get readyState() {
    return this.socket.readyState;
  }

  send(data) {
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log("Websocket Sending message:", data);
        this.socket.send(JSON.stringify(data));
      } else {
        console.error("Socket not open, cannot send message");
      }
    } else {
      console.error("Websocket not initialised.");
    }
  }

  startPing() {
    this.pingInterval = setInterval(() => {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log("Sending ping...");
        this.send({ action: "ping" });
      }
    }, 10000);
  }

  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      alert("Max reconnect attempts reached. Stopping retries.");
      return;
    }

    let timeout = Math.min(5000, 1000 * 2 ** this.reconnectAttempts);
    console.log(`Reconnecting in ${timeout / 1000} seconds...`);
    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, timeout);
  }
}

export function handleSocketMessage(data) {
  switch (data.action) {
    case "start_timers":
      console.log("Received start timers command.");
      handleStartTimersResponse(data);
      break;

    case "pause_timers":
      console.log("Received pause timers command.");
      handlePauseTimersResponse(data);
      break;

    case "pong":
      handlePong(data);
      break;

    case "console.log":
      console.log(data.message);
      break;

    default:
      console.error("Unknown message action:", data.action);
  }
}

export function connectWebsocket() {
  console.log(`profileId: ${window.profile_id}`);
  window.ws = new ProfileWebSocket(window.profile_id);
  window.ws.connect();
}
