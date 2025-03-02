const modal = document.getElementById('quest-modal');

function openModal() {
  modal.style.display = "block";
}

function closeModal() {
  modal.style.display = "none";
}

function showToast(message) {
  const toastContainer = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerText = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
      toast.classList.add("hide");
      setTimeout(() => toast.remove(), 500);
  }, 3000);  // Toast disappears after 3s
}


function showQuestDetails(quest) {
  const dropdown = document.getElementById('quest-durations');
  console.log("quest durations:", quest.duration_choices);
  dropdown.innerHTML = "";
  quest.duration_choices.forEach(choice => {
    let durationText = ""
    if (choice >= 60) {
      durationText = `${Math.round(choice / 60)} minutes`;
    } else {
      durationText = `${choice} seconds`;
    }
    const option = document.createElement('option');
    option.value = choice;
    option.textContent = durationText;
    dropdown.appendChild(option);
  });
  document.getElementById('quest-title').textContent = quest.name;
  document.getElementById('quest-description').textContent = quest.description;
  //document.getElementById('xp-reward-value').textContent = quest.result.xp_reward;
  //document.getElementById('coin-reward-value').textContent = quest.result.coin_reward;
  //const otherRewards = document.getElementById('other-rewards-list');
  //otherRewards.innerHTML = "";
  //Object.entries(quest.result.dynamic_rewards).forEach(([key, value]) => {
  //  const li = document.createElement("li");
  //  li.textContent = `${key}: ${value}`;
  //  otherRewards.appendChild(li);
  //});
  document.querySelectorAll("#quest-list-modal li").forEach(li => li.classList.remove("selected"));
  document.querySelector(`li[data-index="${quest.id}"]`).classList.add("selected");
}

class Quest {
  constructor(id, name, description, intro, outro, stages, currentStageIndex = 0, elapsedTime = 0) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.intro = intro;
    this.outro = outro;
    this.stages = stages;
    this.currentStageIndex = currentStageIndex;
    this.elapsedTime = elapsedTime;
  }

  getCurrentStage() {
    return this.stages[this.currentStageIndex];
  }

  advanceStage() {
    if (this.currentStageIndex < this.stages.length - 1) {
      this.renderPreviousStage();
      this.currentStageIndex++;
      document.getElementById('current-quest-active-stage').textContent = this.stages[this.currentStageIndex].text;
    } else {
      console.log("Quest complete!");
    }
  }

  updateProgress(elapsedTime) {
    while (this.currentStageIndex < this.stages.length - 1 && elapsedTime >= this.stages[this.currentStageIndex].endTime) {
      this.advanceStage();
    }
  }

  renderPreviousStage() {
    const stagesList = document.getElementById('quest-stages-list');
    if (stagesList.style.display == "none") {
      stagesList.style.display = "flex";
    }
    stagesList.innerHTML += `<li>${this.stages[this.currentStageIndex].text}</li>`;
  }

  initialDisplay() {
    document.getElementById('current-quest-title').textContent = this.name;
    //document.getElementById('current-quest-description').textContent = this.description;
    document.getElementById('current-quest-intro').textContent = this.intro;
    console.log("intro text:", this.intro);
    document.getElementById('current-quest-active-stage').textContent = this.getCurrentStage().text;
    document.getElementById('current-quest-outro').textContent = this.outro;
  }

  resetDisplay() {
    const stagesList = document.getElementById('quest-stages-list');
    stagesList.style.display = "none";
    stagesList.innerHTML = "";
    document.getElementById('current-stage-section').style.display = "flex";
  }
}

class EventEmitter {
  constructor() {
    this.events = {};
  }

  // Subscribe to an event
  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }

  // Unsubscribe
  off(event, listener) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(l => l !== listener);
  }

  // Emit
  emit(event, data) {
    if (!this.events[event]) return;
    this.events[event].forEach(listener => listener(data));
  }
}

class Timer extends EventEmitter {
  constructor(displayElementId, mode, status = 'empty', duration = 0) {
    super();
    this.displayElement = document.getElementById(displayElementId);
    this.statusElement = document.getElementById(`${mode}-status-text`);
    this.status = status
    this.duration = duration;
    this.intervalIdTime = null;
    this.startTime = new Date();
    this.elapsedTime = 0; // For countdown timers
    this.remainingTime = duration; // For countdown timers
    this.mode = mode;
  }

  setup(status, elapsedTime, newDuration = this.duration) {
    this.elapsedTime = elapsedTime;
    if (this.mode === "quest") {
      this.remainingTime = newDuration - elapsedTime;
    }
    this.updateStatus(status);
    this.updateDisplay();
  }

  start() {
    if (this.status === 'active') return;
    this.updateStatus("active");
    // Start timer
    this.intervalIdTime = setInterval(() => {
      this.elapsedTime += 1;
      if (this.mode === "quest") {
        this.remainingTime -= 1;
        window.currentQuest.updateProgress(this.elapsedTime);

        if (this.remainingTime <= 0) {
          this.onComplete();
        }
      }
      this.updateDisplay();

    }, 1000);
  }

  stop() {
    if (this.status !== 'active') return;
    this.updateStatus('waiting');
    clearInterval(this.intervalIdTime);
    this.emit('stopped', { timer: this });
  }

  reset() {
    this.stop();
    this.updateStatus('empty');
    this.elapsedTime = 0;
    this.emit('reset', { timer: this });
    this.updateDisplay();
  }

  updateStatus(status) {
    console.log(`${this.mode} timer update status, status: ${status}`);
    this.status = status;
    this.statusElement.innerText = status;
  }

  updateDisplay() {
    const timeToDisplay = this.mode === "quest" ? this.remainingTime : this.elapsedTime;
    const minutes = Math.floor(timeToDisplay / 60);
    const seconds = timeToDisplay % 60;
    this.displayElement.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }

  onComplete() {
    this.stop()
    console.log("Timer complete!");
    this.updateStatus("completed");
    this.emit('completed', { timer: this });
  }
}

function onActivityTimerStopped(data) {
  //window.questTimer.stop();
}

function onActivitySubmitted(data) {
  clearInterval(window.syncInterval);
  window.activityTimer.reset();
  window.activityTimer.updateStatus("completed");
  window.questTimer.stop();
  if (window.questTimer.status !== "completed") {
    window.questTimer.updateStatus("waiting");
  }
  submitActivity();
  //console.log("Clearing sync interval:", window.syncInterval);
}

function onQuestTimerStopped(data) {
  //window.activityTimer.stop();
}

function onQuestCompleted(data) {
  window.activityTimer.stop();
  //window.activityTimer.updateStatus("waiting");
  questCompleted();
  clearInterval(window.syncInterval);
}

function stopClientTimers() {
  window.questTimer.stop();
  window.activityTimer.stop();
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours > 0 ? `${hours}:` : ""}${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function loadQuest(quest_timer) {
  console.log("[LOAD QUEST]")
  const quest = quest_timer.quest;
  //const duration = data.duration;
  window.currentQuest = new Quest(quest.id, quest.name, quest.description, quest.intro_text, quest.outro_text, quest.stages);
  window.currentQuest.initialDisplay();
  window.questSelected = true;
  window.questTimer.setup(quest_timer.status, quest_timer.elapsed_time, quest_timer.duration);
}


// Start timers when both activity and quest are selected
function startTimers() {
  //if (window.activitySelected && window.questSelected) {
  // Change buttons
  document.getElementById('start-activity-btn').style.display = "none";
  document.getElementById('stop-activity-btn').style.display = "flex";
  document.getElementById('stop-activity-btn').removeAttribute("disabled");
  document.getElementById('show-quests-btn-frame').style.display = "none";
  // Start timers
  window.activityTimer.start();
  window.questTimer.start();
  //}
}

function addActivityToList(activity) {
  const activityList = document.getElementById('activity-list');
  const listItem = document.createElement('li');
  // Can't read .name???
  listItem.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
  activityList.prepend(listItem);
  const activitiesTimeMessage = document.getElementById('activities-time-message');
  // Insert text for totals messages
  if (activitiesTimeMessage.innerText == "") {
    activitiesTimeMessage.innerText = "Total time today: "
    document.getElementById('activities-total-message').innerText = "; total activities today: "
  };

  // Update and display totals  
  window.activitiesTime += activity.duration;
  window.activitiesNumber += 1;
  document.getElementById('activities-time-data').innerText = formatDuration(window.activitiesTime);
  document.getElementById('activities-total-data').innerText = window.activitiesNumber;
}

function submitQuestDisplayUpdate() {
  // Change buttons
  document.getElementById('quest-rewards').style.display = "flex";
  document.getElementById('show-quests-btn-frame').style.display = "flex";
  // Reset quest modal details pane
  document.getElementById('quest-title').textContent = "No quest selected";
  document.getElementById('quest-description').textContent = "";
  document.getElementById('xp-reward-value').textContent = "";
  document.getElementById('coin-reward-value').textContent = "";
  document.getElementById('other-rewards-list').innerHTML = "";
  // Display outro message
  document.getElementById('current-quest-outro').style.display = "flex";
}

function loadQuestList(quests) {
  const questList = document.getElementById('quest-list-modal');
  questList.innerHTML = "";
  quests.forEach(quest => {
    const li = document.createElement("li");
    li.textContent = quest.name;
    li.dataset.index = quest.id;
    li.addEventListener("click", () => showQuestDetails(quest));
    questList.appendChild(li);
  });
}

function updatePlayerInfo(profile) {
  document.getElementById('player-name').innerText = profile.name;
  document.getElementById('player-xp').innerText = profile.xp;
  document.getElementById('player-xp-next').innerText = profile.xp_next_level;
  document.getElementById('player-level').innerText = profile.level;
}

function updateCharacterInfo(character) {
  document.getElementById('character-name').innerText = character.name;
  document.getElementById('character-xp').innerText = character.xp;
  document.getElementById('character-xp-next').innerText = character.xp_next_level;
  document.getElementById('character-level').innerText = character.level;
}

function showInput() {
  const startActivityButton = document.getElementById('start-activity-btn');
  startActivityButton.removeAttribute("disabled");
  startActivityButton.style.display = "flex";
  const stopActivityButton = document.getElementById('stop-activity-btn');
  stopActivityButton.setAttribute("disabled", true);
  stopActivityButton.style.display = "none";

  document.getElementById('activity-input-div').style.display = "flex";
}

function hideInput() {
  const startActivityButton = document.getElementById('start-activity-btn');
  startActivityButton.setAttribute("disabled", true);
  startActivityButton.style.display = "none";
  const stopActivityButton = document.getElementById('stop-activity-btn');
  stopActivityButton.removeAttribute("disabled");
  stopActivityButton.style.display = "flex";
}

function showQuests() {
  document.getElementById('show-quests-btn-frame').style.display = "none";
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Validate input
function validateInput(input) {
  const pattern = /^[a-zA-Z0-9\s]+$/; // Adjust pattern as needed
  return pattern.test(input);
}


///////////////////////////
// AJAX REQUEST FUNCTIONS
///////////////////////////


async function createActivityTimer() {
  const activityInput = document.getElementById('activity-input');
  if (!validateInput(activityInput.value)) {
    alert("Invalid input. Please use only letters, numbers, and spaces.");
    return;
  }
  try {
    const response = await fetch("/create_activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value })
    });
    const data = await response.json();
    handleCreateActivityResponse(data);

  } catch (e) {
    console.error('Error:', e);
  }
}

async function submitActivity(event) {
  const activityInput = document.getElementById('activity-input');
  try {
    const response = await fetch("/submit_activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
    await checkResponse(response);
    const data = await response.json();
    handleSubmitActivityResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

async function chooseQuest(event) {
  event.preventDefault();
  if (window.currentQuest) {
    window.currentQuest.resetDisplay();
  }
  try {
    const selectedQuest = document.querySelector('#quest-list-modal .selected');
    if (!selectedQuest) {
      alert("Please select a quest first.");
      return;
    }
    const questId = selectedQuest.dataset.index;
    console.log("chooseQuest(), questId:", questId);
    const selectedDuration = document.getElementById('quest-durations');
    if (!selectedDuration) {
      alert("Please select a duration for your quest.");
      return;
    }
    const response = await fetch("/choose_quest/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "quest_id": questId, "duration": selectedDuration.value })
    });
    await checkResponse(response);

    const data = await response.json();
    handleChooseQuestResponse(data);

  } catch (e) {
    console.error('Error:', e);
  }
}

// Submit quest
async function questCompleted() {
  try {
    const response = await fetch('/quest_completed/', {
      method: 'POST',
    });
    //console.log('response ok:', response.ok);
    await checkResponse(response);
    const data = await response.json();
    handleQuestCompletedResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

async function startTimersOld() {
  try {
    const response = await fetch("/start_timers/", {
      method: 'POST',
    });
    await checkResponse(response);
    const data = await response.json();
    handleStartTimersResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function handleStartTimersResponse(data) {
  if (data.success) {
    console.log(data.message);

  } else {
    console.error(data.message);

  }
}




// Fetch activities
async function fetchActivities() {
  try {
    const response = await fetch('/fetch_activities/', {
      method: 'GET',
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchActivitiesResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

// Fetch eligible quests
async function fetchQuests() {
  try {
    const response = await fetch('/fetch_quests/', {
      method: 'GET',
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchQuestsResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

// Fetch player & char info
async function fetchInfo() {
  try {
    const response = await fetch('/fetch_info/', {
      method: 'GET',
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchInfoResponse(data);
  } catch (e) {
    console.error('There was a problem:', e);
  }
}


//////////////////////////////////////////////
// RESPONSE HANDLER FUNCTIONS ////////////////
//////////////////////////////////////////////


function handleCreateActivityResponse(data) {
  if (data.success) {
    window.activitySelected = true;
    window.activityTimer.updateStatus("waiting");
    document.getElementById('start-activity-btn').setAttribute("disabled", true);
    if (data.action == 'start_timers') {
      startTimers();
    }

  } else {
    console.error(data.message);
  }
}

function handleUpdateActivityNameResponse(data) {
  if (data.success) {
    console.log("Activity name updated:", data.new_name)
  } else {
    console.error(data.message);
  }
}

function handleSubmitActivityResponse(data) {
  if (data.success) {
    console.log("Activities response:", data.activities[0]);
    addActivityToList(data.activities[0]);
    showInput();
    window.activityTimer.reset();
    window.activitySelected = false;
    updatePlayerInfo(data.profile);
    document.getElementById('activity-input').value = "";
  } else {
    console.error(data.message);
  }
}

function handleChooseQuestResponse(data) {
  if (data.success) {
    // Reset quest display
    document.getElementById('quest-rewards').style.display = "none";
    document.getElementById('current-quest-outro').style.display = "none";

    loadQuest(data.quest_timer);
    closeModal();
    if (data.action === 'start_timers') {
      startTimers();
    }
  } else {
    document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
  }
}

function handleQuestCompletedResponse(data) {
  if (data.success) {
    console.log(`[QUEST COMPLETE RESPONSE] Server timer status: ${data.activity_timer_status}/${data.quest_timer_status}`);
    submitQuestDisplayUpdate();
    window.questSelected = false;
    window.currentQuest.renderPreviousStage();
    document.getElementById('current-stage-section').style.display = "none";
    updateCharacterInfo(data.character);
    loadQuestList(data.quests);
  } else {
    console.error(data.message);
  }
}

function handleFetchActivitiesResponse(data) {
  if (data.success) {
    const activities = data.activities;
    const activityList = document.getElementById('activity-list');
    activityList.innerHTML = '';
    window.activitiesNumber = 0;
    window.activitiesTime = 0;

    activities.forEach(activity => {
      window.activitiesNumber += 1;
      window.activitiesTime += activity.duration;
      const li = document.createElement('li');
      li.id = `activity-${activity.id}`;
      li.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
      activityList.appendChild(li);
    });
    const activityTimeMessage = document.getElementById('activities-time-message');
    if (activityTimeMessage.innerText == "") {
      activityTimeMessage.innerText = "Total time today: ";
      document.getElementById('activities-total-message').innerText = "; total activities today: ";
    }
    document.getElementById('activities-time-data').innerText = formatDuration(window.activitiesTime);
    document.getElementById('activities-total-data').innerText = window.activitiesNumber;
  } else {
    console.error(data.message);
  }
}

function handleFetchQuestsResponse(data) {
  if (data.success) {
    loadQuestList(data.quests);
  } else {
    console.error(data.message);
  }
}

function handleFetchInfoResponse(data) {
  if (data.success) {
    window.profile_id = data.profile.id;
    const activity_timer = data.activity_timer;
    const quest_timer = data.quest_timer;
    console.log("Data:", data);
    console.log("Activity timer:", activity_timer);
    console.log("Quest timer:", quest_timer);
    updatePlayerInfo(data.profile);
    updateCharacterInfo(data.character);
    if (activity_timer.status !== "empty") {
      document.getElementById('activity-input').value = activity_timer.activity.name;
      console.log("Activity time from server:", activity_timer.elapsed_time);
      console.log("Activity timer before:", window.activityTimer);
      window.activityTimer.setup(activity_timer.status, activity_timer.elapsed_time);
      console.log("Activity timer after:", window.activityTimer);
      window.activitySelected = true;
      window.activityTimer.updateStatus(activity_timer.status)
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
    if (data.action == "start_timers") {
      startTimers();
    }
  } else {
    console.error(data.message);
  }
}


async function checkResponse(response) {
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response;
}

////////////////////////////////
/////// EVENT LISTENERES //////
//////////////////////////////

document.addEventListener('DOMContentLoaded', () => {
  initialiseTimers();
  setupEventListeners();
  updateUI();
  startHeartbeat();
});

function initialiseTimers() {
  window.activityTimer = new Timer('activity-timer', "activity", 0);
  window.questTimer = new Timer('quest-timer', "quest", 0);
  window.activitySelected = false;
  window.questSelected = false;
}

function setupEventListeners() {
  document.getElementById("start-activity-btn").addEventListener("click", createActivityTimer);
  document.getElementById('show-quests-btn').addEventListener('click', openModal);
  document.getElementById('close-modal-btn').addEventListener('click', closeModal);
  document.getElementById('quest-modal').addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
  document.getElementById('choose-quest-btn').addEventListener('click', chooseQuest);
  document.getElementById("stop-activity-btn").addEventListener("click", onActivitySubmitted);
  window.questTimer.on('completed', onQuestCompleted);


}

function updateUI() {
  // Update the UI with current timer status, or any other necessary state
  console.log("When does THIS happen");
  document.getElementById('activity-timer').textContent = window.activityTimer.elapsedTime;
  //document.getElementById(window.activityTimer.displayElement).textContent = window.activityTimer.elapsedTime;
  window.activityTimer.updateDisplay();
  document.getElementById('quest-timer').textContent = window.questTimer.remainingTime;
  //document.getElementById(window.questTimer.displayElement).textContent = window.questTimer.remainingTime;
  window.questTimer.updateDisplay();
  fetchActivities();
  fetchQuests();
  fetchInfo();
}

function startHeartbeat(maxFailures = 3) {
  let failureCount = 0;
  let heartbeatInterval;
  async function sendHeartbeat() {
    try {
      console.log('Sending heartbeat');
      const response = await fetch('/heartbeat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activity: window.activitySelected,
          quest: window.questSelected,
        }),
      });
      const data = await response.json();

      handleHeartbeatResponse(data);

      failureCount = 0;
    } catch (e) {
      console.error('Heartbeat failed:', e);
      failureCount++;
      if (failureCount >= maxFailures) {
        console.error('Max heartbeat failures reached. Stopping heartbeat')
        stopHeartbeat();
      }
    }
  }

  function handleHeartbeatResponse(data) {
    if (data.success) {
      console.log(`[HEARTBEAT RESPONSE] Server timer status: ${data.activity_timer_status}/${data.quest_timer_status}`);
      if (data.status === 'quest_completed') {
        window.questTimer.onComplete();
      }
    } else {
      console.error(data.message);
    }
  }

  function stopHeartbeat() {
    clearInterval(heartbeatInterval);
    console.warn('Client heartbeat stopped');
  }

  heartbeatInterval = setInterval(sendHeartbeat, 5000);
}