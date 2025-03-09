import { addActivityToList } from './activityHandlers.js';
import { updatePlayerInfo, updateCharacterInfo } from '../utils/domUtils.js';
import { loadQuest, loadQuestList } from './questHandlers.js';

export function handleCreateActivityResponse(data) {
  if (data.success) {
    window.activitySelected = true;
    window.activityTimer.updateStatus("waiting");
    document.getElementById("start-activity-btn").setAttribute("disabled", true);
  } else {
    console.error(data.message);
  }
}

export function handleUpdateActivityNameResponse(data) {
  if (data.success) {
    console.log("Activity name updated:", data.new_name);
  } else {
    console.error(data.message);
  }
}

export function handleSubmitActivityResponse(data) {
  if (data.success) {
    addActivityToList(data.activities[0]);
    showInput();
    window.activityTimer.reset();
    window.activitySelected = false;
    updatePlayerInfo(data.profile);
    document.getElementById("activity-input").value = "";
  } else {
    console.error(data.message);
  }
}

export function handleChooseQuestResponse(data) {
  if (data.success) {
    document.getElementById("quest-rewards").style.display = "none";
    document.getElementById("current-quest-outro").style.display = "none";
    loadQuest(data.quest_timer);
    closeModal();
  } else {
    document.getElementById("feedback-message").textContent = "Quest selection failed, please try again.";
  }
}

export function handleCompleteQuestResponse(data) {
  if (data.success) {
    console.log(`[QUEST COMPLETE RESPONSE] Server timer status: ${data.activity_timer_status}/${data.quest_timer_status}`);
    submitQuestDisplayUpdate();
    window.questSelected = false;
    window.currentQuest.renderPreviousStage();
    document.getElementById("current-stage-section").style.display = "none";
    updateCharacterInfo(data.character);
    loadQuestList(data.quests);
  } else {
    console.error(data.message);
  }
}

export function handleFetchActivitiesResponse(data) {
  if (data.success) {
    const activities = data.activities;
    const activityList = document.getElementById("activity-list");
    activityList.innerHTML = "";
    window.activitiesNumber = 0;
    window.activitiesTime = 0;

    activities.forEach((activity) => {
      window.activitiesNumber += 1;
      window.activitiesTime += activity.duration;
      const li = document.createElement("li");
      li.id = `activity-${activity.id}`;
      li.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
      activityList.appendChild(li);
    });

    const activityTimeMessage = document.getElementById("activities-time-message");
    if (activityTimeMessage.innerText === "") {
      activityTimeMessage.innerText = "Total time today: ";
      document.getElementById("activities-total-message").innerText = "; total activities today: ";
    }

    document.getElementById("activities-time-data").innerText = formatDuration(window.activitiesTime);
    document.getElementById("activities-total-data").innerText = window.activitiesNumber;
  } else {
    console.error(data.message);
  }
}

export function handleFetchQuestsResponse(data) {
  if (data.success) {
    loadQuestList(data.quests);
  } else {
    console.error(data.message);
  }
}

export function handleFetchInfoResponse(data) {
  if (data.success) {
    window.profile_id = data.profile.id;
    connectWebsocket();
    const activity_timer = data.activity_timer;
    const quest_timer = data.quest_timer;

    updatePlayerInfo(data.profile);
    updateCharacterInfo(data.character);

    if (activity_timer.status !== "empty") {
      document.getElementById("activity-input").value = activity_timer.activity.name;
      window.activityTimer.setup(activity_timer.status, activity_timer.elapsed_time);
      window.activitySelected = true;
      window.activityTimer.updateStatus(activity_timer.status);
      hideInput();
    } else {
      window.activitySelected = false;
    }

    console.log("[FETCH INFO RESPONSE] Quest status:", quest_timer.status);
    if (quest_timer.status !== "empty") {
      loadQuest(data.quest_timer);
    } else {
      window.questSelected = false;
    }
  } else {
    console.error(data.message);
  }
}


}
