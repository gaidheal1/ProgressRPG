import { createActivityTimer, submitActivity } from '../api/activityApi.js';
import { formatDuration } from '../utils/format.js'

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

export function addActivityToList(activity) {
  const activityList = document.getElementById("activity-list");
  const listItem = document.createElement("li");
  listItem.textContent = `${activity.name} - ${formatDuration(
    activity.duration
  )}`;
  activityList.prepend(listItem);

  const activitiesTimeMessage = document.getElementById(
    "activities-time-message"
  );
  // Insert text for totals messages
  if (activitiesTimeMessage.innerText == "") {
    activitiesTimeMessage.innerText = "Total time today: ";
    document.getElementById("activities-total-message").innerText =
      "; total activities today: ";
  }

  // Update and display totals
  window.activitiesTime += activity.duration;
  window.activitiesNumber += 1;
  document.getElementById("activities-time-data").innerText = formatDuration(
    window.activitiesTime
  );
  document.getElementById("activities-total-data").innerText =
    window.activitiesNumber;
}
