export function onActivitySubmitted(data) {
  ws.pauseTimers();

  window.activityTimer.reset();
  window.activityTimer.updateStatus("completed");
  window.questTimer.pause();

  if (window.questTimer.status !== "completed") {
    window.questTimer.updateStatus("waiting");
  }
  submitActivity();
}

export function onQuestCompleted(data) {
  ws.pauseTimers();
  window.activityTimer.pause();
  completeQuest();
}
