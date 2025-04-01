import { checkResponse } from '../utils/httpUtils.js'

export async function chooseQuest() {
  if (window.currentQuest) window.currentQuest.resetDisplay();

  try {
    const selectedQuest = document.querySelector("#quest-list-modal .selected");
    if (!selectedQuest) {
      alert("Please select a quest first.");
      return;
    }
    const questId = selectedQuest.dataset.index;
    const selectedDuration = document.getElementById("quest-durations");
    if (!selectedDuration) {
      alert("Please select a duration for your quest.");
      return;
    }

    const response = await fetch("/choose_quest/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        quest_id: questId,
        duration: selectedDuration.value,
      }),
    });

    await checkResponse(response);
    const data = await response.json();
    handleChooseQuestResponse(data);
  } catch (e) {
    console.error("Error choosing quest:", e);
  }
}

export async function completeQuest() {
  try {
    const response = await fetch("/complete_quest/", { method: "POST" });
    await checkResponse(response);
    const data = await response.json();

    handleCompleteQuestResponse(data);
    localStorage.removeItem("pendingQuest");
  } catch (e) {
    console.error("Error completing quest:", e);
    localStorage.setItem("pendingQuest", JSON.stringify(true));
    console.warn("Quest completion failed. It will be retried later.");
  }
}

export async function fetchQuests() {
  try {
    const response = await fetch("/fetch_quests/", { method: "GET" });
    await checkResponse(response);
    const data = await response.json();
    handleFetchQuestsResponse(data);
  } catch (e) {
    console.error("Error fetching quests:", e);
  }
}
