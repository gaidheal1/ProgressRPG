import { Timer } from '../modules/Timer.js';

export function startTimers() {
  // Change buttons
  document.getElementById("start-activity-btn").style.display = "none";
  document.getElementById("stop-activity-btn").style.display = "flex";
  document.getElementById("stop-activity-btn").removeAttribute("disabled");
  document.getElementById("show-quests-btn-frame").style.display = "none";
  // Start timers
  window.activityTimer.start();
  window.questTimer.start();
}

export function pauseTimers() {
  // Change buttons

  // Pause timers
  window.activityTimer.pause();
  window.questTimer.pause();
}
