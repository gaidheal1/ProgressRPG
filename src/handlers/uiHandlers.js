import { fetchActivities } from '../api/activityApi.js';
import { fetchQuests } from '../api/questApi.js';
import { fetchInfo } from '../api/userApi.js';

export function updateUI() {
  console.log("Updating UI");

  // Update timer displays
  document.getElementById("activity-timer").textContent = window.activityTimer.elapsedTime;
  window.activityTimer.updateDisplay();

  document.getElementById("quest-timer").textContent = window.questTimer.remainingTime;
  window.questTimer.updateDisplay();

  // Fetch initial data
  fetchActivities();
  fetchQuests();
  fetchInfo();
}

export function openModal() {
  const modal = document.getElementById("quest-modal");
  modal.style.display = "block";
}

export function closeModal() {
  const modal = document.getElementById("quest-modal");
  modal.style.display = "none";
}

export function showToast(message) {
  const toastContainer = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerText = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 500);
  }, 3000); // Toast disappears after 3s
}
