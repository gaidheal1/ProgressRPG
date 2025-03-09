import { createActivityTimer } from '../api/activityApi.js';
import { chooseQuest } from '../api/questApi.js';
import { openModal, closeModal } from '../handlers/uiHandlers.js';
import { onActivitySubmitted, onQuestCompleted } from '../handlers/eventHandlers.js';

export function setupEventListeners() {
  document
    .getElementById("start-activity-btn")
    .addEventListener("click", createActivityTimer);

  document
    .getElementById("show-quests-btn")
    .addEventListener("click", openModal);

  document
    .getElementById("close-modal-btn")
    .addEventListener("click", closeModal);

  document.getElementById("quest-modal").addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  document
    .getElementById("choose-quest-btn")
    .addEventListener("click", chooseQuest);

  document
    .getElementById("stop-activity-btn")
    .addEventListener("click", onActivitySubmitted);

  window.questTimer.on("completed", onQuestCompleted);
}
