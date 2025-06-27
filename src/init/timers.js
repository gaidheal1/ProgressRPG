export function initialiseTimers() {
  window.activityTimer = new Timer("activity-timer", "activity", 0);
  window.questTimer = new Timer("quest-timer", "quest", 0);
  window.activitySelected = false;
  window.questSelected = false;
}
