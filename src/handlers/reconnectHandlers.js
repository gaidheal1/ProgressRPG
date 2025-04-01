import { submitActivity } from '../api/activityApi.js';
import { completeQuest } from '../api/questApi.js';

export function handleReconnect() {
  const pendingActivity = localStorage.getItem("pendingActivity");
  if (pendingActivity) {
    console.log("Found pending activity, attempting to resubmit...");
    submitActivity();
  }

  const pendingQuest = localStorage.getItem("pendingQuest");
  if (pendingQuest) {
    console.log("Found pending quest, attempting to resubmit...");
    completeQuest();
  }
}
