import { EventEmitter } from './EventEmitter.js';

export class Timer extends EventEmitter {
  constructor(displayElementId, mode, status = "empty", duration = 0) {
    super();
    this.displayElement = document.getElementById(displayElementId);
    this.statusElement = document.getElementById(`${mode}-status-text`);
    this.status = status;
    this.duration = duration;
    this.intervalIdTime = null;
    this.startTime = new Date();
    this.elapsedTime = 0; // For countdown timers
    this.remainingTime = duration; // For countdown timers
    this.mode = mode;
  }

  setup(status, elapsedTime, newDuration = this.duration) {
    this.elapsedTime = elapsedTime;
    if (this.mode === "quest") {
      this.remainingTime = newDuration - elapsedTime;
    }
    this.updateStatus(status);
    this.updateDisplay();
  }

  start() {
    console.log(`${this.mode} timer start method. Status: ${this.status}`);
    if (this.status === "active") return;
    this.updateStatus("active");
    // Start timer
    this.intervalIdTime = setInterval(() => {
      this.elapsedTime += 1;
      if (this.mode === "quest") {
        this.remainingTime -= 1;
        window.currentQuest.updateProgress(this.elapsedTime);

        if (this.remainingTime <= 0) {
          this.onComplete();
        }
      }
      this.updateDisplay();
    }, 1000);
  }

  pause() {
    console.log(`${this.mode} timer start method. Status: ${this.status}`);
    if (this.status !== "active") return;
    this.updateStatus("waiting");
    clearInterval(this.intervalIdTime);
    this.emit("paused", { timer: this });
  }

  reset() {
    this.pause();
    this.updateStatus("empty");
    this.elapsedTime = 0;
    this.emit("reset", { timer: this });
    this.updateDisplay();
  }

  updateStatus(status) {
    console.log(`${this.mode} timer update status, status: ${status}`);
    this.status = status;
    this.statusElement.innerText = status;
  }

  updateDisplay() {
    const timeToDisplay =
      this.mode === "quest" ? this.remainingTime : this.elapsedTime;
    const minutes = Math.floor(timeToDisplay / 60);
    const seconds = timeToDisplay % 60;
    this.displayElement.textContent = `${minutes}:${seconds
      .toString()
      .padStart(2, "0")}`;
  }

  onComplete() {
    this.pause();
    console.log("Timer complete!");
    this.updateStatus("completed");
    this.emit("completed", { timer: this });
  }
}
