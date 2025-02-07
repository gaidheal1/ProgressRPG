const modal = document.getElementById('quest-modal');

function openModal() {
  modal.style.display = "block";
}

function closeModal() {
  modal.style.display = "none";
}

function showQuestDetails(quest) {
  const durationList = document.getElementById('quest-duration');
  console.log("quest durations:", quest.duration_choices); // currently undefined
  document.getElementById('quest-title').textContent = quest.name;
  document.getElementById('quest-description').textContent = quest.description;
  //document.getElementById('xp-reward-value').textContent = quest.result.xp_reward;
  //document.getElementById('coin-reward-value').textContent = quest.result.coin_reward;
  const otherRewards = document.getElementById('other-rewards-list');
  otherRewards.innerHTML = "";
  //Object.entries(quest.result.dynamic_rewards).forEach(([key, value]) => {
  //  const li = document.createElement("li");
  //  li.textContent = `${key}: ${value}`;
  //  otherRewards.appendChild(li);
  //});
  document.querySelectorAll(".quest-list-modal li").forEach(li => li.classList.remove("selected"));
  document.querySelector(`li[data-index="${quest.id}"]`).classList.add("selected");
}

class Quest {
  constructor(id, name, description, intro, outro, duration, stages, currentStageIndex = 0, elapsedTime = 0) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.intro = intro;
    this.outro = outro;
    this.duration = duration;
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
  constructor(displayElementId, mode, duration = 0) {
    super();
    this.displayElement = document.getElementById(displayElementId);
    this.duration = duration;
    this.intervalIdTime = null;
    this.intervalIdSync = null;
    this.startTime = new Date();
    this.elapsedTime = 0; // For countdown timers
    this.remainingTime = duration; // For countdown timers
    this.isRunning = false; // Timer state
    this.mode = mode;
  }

  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    // Start timer
    this.intervalIdTime = setInterval(() => {
      this.elapsedTime += 1;
      if (this.mode === "quest") {
        this.remainingTime -= 1;
        window.currentQuest.updateProgress(this.elapsedTime);

        if (this.remainingTime <= 0) {
          this.stop();
          this.onComplete();
        }
      }
      this.updateDisplay();
    }, 1000);
    // Start sync timer
    this.intervalIdSync = setInterval(() => {
      syncTimer(this.mode);
      //const diff = serverTime - this.elapsedTime;
      //console.log("diff", diff)
    }, 3000); // 300000 for 5 minutes, smaller for testing
  }

  stop() {
    if (!this.isRunning) return;
    this.isRunning = false;
    clearInterval(this.intervalIdTime);
    this.emit('stopped', { timer: this });
    clearInterval(this.intervalIdSync);
  }

  reset(newDuration = this.duration, elapsedTime = 0) {
    this.stop();
    this.elapsedTime = elapsedTime;
    this.remainingTime = this.mode === "quest" ? newDuration : 0;
    this.updateDisplay();
    this.emit('reset', { timer: this });
  }

  updateDisplay() {
    const timeToDisplay = this.mode === "quest" ? this.remainingTime : this.elapsedTime;
    const minutes = Math.floor(timeToDisplay / 60);
    const seconds = timeToDisplay % 60;
    this.displayElement.textContent = `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }

  onComplete() {
    console.log("Timer complete!");
    this.emit('completed', { timer: this });
  }

  async syncWithServer(endpoint, csrfToken) {
    const data = this.mode === "quest" ? { remaining_time: this.remainingTime } : { elapsed_time: this.elapsedTime };

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      console.log("Timer synced with server.");
    } else {
      console.error("Failed to sync timer with server.");
    }
  }
}

function onActivityTimerStopped(data) {
  window.questTimer.stop();
}

function onActivitySubmitted(data) {
  window.activityTimer.reset();
  window.questTimer.stop();
  submitActivity();
}

function onQuestTimerStopped(data) {
  window.activityTimer.stop();
}

function onQuestCompleted(data) {
  window.activityTimer.stop();
  submitQuest();
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours > 0 ? `${hours}:` : ""}${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function loadQuest(quest) {
  window.currentQuest = new Quest(quest.id, quest.name, quest.description, quest.intro_text, quest.outro_text, quest.duration, quest.stages);
  window.currentQuest.initialDisplay();
  window.questSelected = true;
  window.questTimer.reset(window.currentQuest.duration);
}

// Start timers when both activity and quest are selected
function startTimerIfReady() {
  if (window.activitySelected && window.questSelected) {

    // Change buttons
    document.getElementById('start-activity-btn').style.display = "none";
    document.getElementById('stop-activity-btn').style.display = "flex";
    document.getElementById('stop-activity-btn').removeAttribute("disabled");
    document.getElementById('show-quests-btn-frame').style.display = "none";
    // Update statuses
    document.getElementById('activity-status-text').innerText = "running";
    document.getElementById('quest-status-text').innerText = "running";

    window.activityTimer.start();
    window.questTimer.start();
    startTimer("activity");
    startTimer("quest");
  }
}

function addActivityToList(activity) {
  const activityList = document.getElementById('activity-list');
  const listItem = document.createElement('li');
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
  // Update statuses
  document.getElementById('activity-status-text').innerText = "waiting";
  document.getElementById('quest-status-text').innerText = "finished";
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

  document.getElementById('activity-input-div').style.display = "none";
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


//
// AJAX REQUEST FUNCTIONS
//


async function createActivityTimer() {
  const activityInput = document.getElementById('activity-input');
  if (!validateInput(activityInput.value)) {
    alert("Invalid input. Please use only letters, numbers, and spaces.");
    return;
  }
  try {
    const response = await fetch("/create_activity_timer/", {
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
  event.preventDefault();
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
    const response = await fetch("/choose_quest/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "quest_id": questId })
    });
    await checkResponse(response);

    const data = await response.json();
    handleChooseQuestResponse(data);
    startTimerIfReady();
  } catch (e) {
    console.error('Error:', e);
  }
}

// Submit quest
async function submitQuest() {
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

async function startTimer(mode) {
  try {
    const response = await fetch("/start_timer/", {
      method: 'POST',
      headers: { "Content-Type": "text/plain" },
      body: mode,
    });
    await checkResponse(response);

    const data = await response.json();
    if (data.success) {
      console.log(data.message);
    } else {
      console.error(data.message);
    }
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

// Check state
async function syncTimer(mode) {
  try {
    const response = await fetch("/get_timer_state/", {
      method: 'POST',
      headers: { "Content-Type": "text/plain" },
      body: mode,
    });
    await checkResponse(response);
    const data = await response.json();
    if (data.success) {
      if (mode == "activity") {
        const diff = Math.abs(data.timer.duration - window.activityTimer.elapsedTime);
        if (diff > 10) {
          window.activityTimer.elapsedTime = Math.floor(data.timer.duration);
        }
        //return data.timer.duration
      } else if (mode == "quest") {
        console.log('quest duration:', data.timer.duration);

        //return data.timer.remaining_time;
      }
    } else {
      console.error(data.message);
    }
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

async function stopTimer(mode) {
  try {
    const response = await fetch("/stop_timer/", {
      method: 'POST',
      headers: { "Content-Type": "text/plain" },
      body: mode,
    });
    await checkResponse(response);
    const data = await response.json();
    if (data.success) {
      console.log(data.message);
    } else {
      console.error(data.message);
    }
  } catch (e) {
    console.error('There was a problem:', e);
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
    startTimerIfReady();
    document.getElementById('start-activity-btn').setAttribute("disabled", true);
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
    addActivityToList(data.activities[0]);
    showInput();
    window.activityTimer.reset();
    window.activitySelected = false;
    updatePlayerInfo(data.profile);
    document.getElementById('activity-input').value = "";
    document.getElementById('activity-status-text').innerText = "finished";
    document.getElementById('quest-status-text').innerText = "waiting";
  } else {
    console.error(data.message);
  }
}

function handleChooseQuestResponse(data) {
  if (data.success) {
    document.getElementById('quest-rewards').style.display = "none";
    document.getElementById('current-quest-outro').style.display = "none";
    loadQuest(data.quest);
    closeModal();
    startTimerIfReady();
      }
  } else {
    document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
  }
}

function handleQuestCompletedResponse(data) {
  if (data.success) {
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
    if (activities.length == 0) {
      activityList.innerText = "No activities done today!";
    } else {
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
    }
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

    updatePlayerInfo(data.profile);
    updateCharacterInfo(data.character);
    if (data.current_activity) {
      document.getElementById('activity-input').value = data.current_activity.name;
      //window.activityTimer.reset(elapsedTime = data.current_activity.duration);
      window.activitySelected = true;
      hideInput();
    } else {
      window.activitySelected = false;
    }
    if (data.current_quest) {
      loadQuest(data.current_quest);
      //window.questTimer.reset(elapsedTime = data.current_quest.elapsed_time);
      window.questSelected = true;
    } else {
      window.questSelected = false;
    }

    startTimerIfReady();
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
  document.getElementById("stop-activity-btn").addEventListener("click", submitActivity);

  window.activityTimer.on('completed', onActivitySubmitted);
  window.questTimer.on('completed', onQuestCompleted);

  
}

function updateUI() {
  // Update the UI with current timer status, or any other necessary state
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

function startHeartbeat() {
  setInterval(async () => {
    try {
      await fetch('/heartbeat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activity: window.activitySelected,
          quest: window.questSelected,
        }),
      });
    } catch (e) {
      console.error('Heartbeat failed:', e);
    }
  }, 5000); // Send heartbeat every 5 seconds
}