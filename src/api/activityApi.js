import { validateInput } from '../utils/validate.js';
import { checkResponse } from '../utils/httpUtils.js';

export async function createActivityTimer() {
  const activityInput = document.getElementById("activity-input");
  if (!validateInput(activityInput.value)) {
    alert("Invalid input. Please use only letters, numbers, and spaces.");
    return;
  }
  try {
    const response = await fetch("/create_activity/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
    const data = await response.json();
    handleCreateActivityResponse(data);
  } catch (e) {
    console.error("Error creating activity timer:", e);
  }
}

export async function submitActivity() {
  const activityInput = document.getElementById("activity-input");
  let activity = localStorage.getItem("pendingActivity")
    ? JSON.parse(localStorage.getItem("pendingActivity"))
    : { name: activityInput.value };

  try {
    const response = await fetch("/submit_activity/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(activity),
    });
    await checkResponse(response);
    const data = await response.json();

    handleSubmitActivityResponse(data);
    localStorage.removeItem("pendingActivity");
  } catch (e) {
    console.error("Error submitting activity:", e);
    localStorage.setItem("pendingActivity", JSON.stringify(activity));
    console.warn("Activity submission failed. It will be retried later.");
  }
}

export async function fetchActivities() {
  try {
    const response = await fetch("/fetch_activities/", { method: "GET" });
    await checkResponse(response);
    const data = await response.json();
    handleFetchActivitiesResponse(data);
  } catch (e) {
    console.error("Error fetching activities:", e);
  }
}
