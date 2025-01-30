document.addEventListener('DOMContentLoaded', async () => {
  await openSocket();
  initialiseTimers();
  setupEventListeners();
  await updateUI();

});

async function openSocket() {
  window.socket = new ProfileWebSocket(window.profile_id);
  window.socket.connect();
  await new Promise((resolve) => {
    window.socket.onopen = () => {
      console.log("Connected to timer socket");
      resolve();
    };
  });
}

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

async function updateUI() {
  // Update the UI with current timer status, or any other necessary state
  document.getElementById('activity-timer').textContent = window.activityTimer.elapsedTime;
  //document.getElementById(window.activityTimer.displayElement).textContent = window.activityTimer.elapsedTime;
  window.activityTimer.updateDisplay();
  document.getElementById('quest-timer').textContent = window.questTimer.remainingTime;
  //document.getElementById(window.questTimer.displayElement).textContent = window.questTimer.remainingTime;
  window.questTimer.updateDisplay();
  if (window.socket.readyState === WebSocket.OPEN) {
    await fetchActivities();
    await fetchQuests();
    await fetchInfo();
  } else {
    console.error("Socket not open");
  }
  
}


const modal = document.getElementById('quest-modal');

function openModal() {
  modal.style.display = "block";
}

function closeModal() {
  modal.style.display = "none";
}

function showQuestDetails(quest) {
  document.getElementById('quest-title').textContent = quest.name;
  document.getElementById('quest-description').textContent = quest.description;
  document.getElementById('xp-reward-value').textContent = quest.result.xp_reward;
  document.getElementById('coin-reward-value').textContent = quest.result.coin_reward;
  const otherRewards = document.getElementById('other-rewards-list');
  otherRewards.innerHTML = "";
  Object.entries(quest.result.dynamic_rewards).forEach(([key, value]) => {
    const li = document.createElement("li");
    li.textContent = `${key}: ${value}`;
    otherRewards.appendChild(li);
  });
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
    this.elapsedTime = elapsedTime;
    while (this.currentStageIndex < this.stages.length - 1 && this.elapsedTime >= this.stages[this.currentStageIndex].endTime) {
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
    document.getElementById('current-quest-description').textContent = this.description;
    document.getElementById('current-quest-intro').textContent = this.intro;
    document.getElementById('current-quest-outro').textContent = this.outro;
  }

  resetDisplay() {
    const stagesList = document.getElementById('quest-stages-list');
    stagesList.style.display = "none";
    stagesList.innerHTML = "";
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
  constructor(displayElementId, mode) {
    super();
    this.displayElement = document.getElementById(displayElementId);
    this.mode = mode;
    this.elapsedTime = 0;
    this.remainingTime = 0;
    this.is_running = false;

  }

  start() {
    if (this.is_running) return;
    if (this.remainingTime <= 0 && this.mode === "quest") {
      console.error("Cannot start quest timer with non-positive remaining time");
      return;
    }
    this.is_running = true;
    this.emit('start', { timer: this });
    this.interval = setInterval(() => {
      if (this.mode === "quest") {
        this.remainingTime -= 1;
        if (this.remainingTime <= 0) {
          this.remainingTime = 0;
          this.stop();
          this.onComplete();
        }
      }
      this.elapsedTime += 1;
      this.updateDisplay();
    }, 1000);
  }

  stop() {
    if (!this.is_running) return;
    this.is_running = false;
    clearInterval(this.interval);
    this.emit('stop', { timer: this });
  }

  startFromState(elapsedTime, remainingTime) {
    if (this.mode === "quest") {
      this.remainingTime = remainingTime;
    }
    this.elapsedTime = elapsedTime;
    this.updateDisplay();
  }

  reset() {
    this.stop();
    this.updateDisplay();
    this.emit('reset', { timer: this });
  }

  updateDisplay() {
    this.displayElement.textContent = formatDuration(this.mode === "quest" ? this.remainingTime : this.elapsedTime);
  }

  onComplete() {
    console.log("Timer complete!");
    this.emit('completed', { timer: this });
  }
}

function onActivityTimerStopped(data) {
  window.questTimer.stop();
}

function onActivitySubmitted(data) {
  window.activityTimer.reset();
  window.questTimer.stop();
  window.socket.stopTimers();
  submitActivity();
}

function onQuestTimerStopped(data) {
  window.activityTimer.stop();
}

function onQuestCompleted(data) {
  window.activityTimer.stop();
  window.socket.stopTimers();
  submitQuest();
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours > 0 ? `${hours}:` : ""}${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

async function createActivityTimer() {
  const activityInput = document.getElementById('activity-input');
  const csrftoken = getCookie('csrftoken');
  if (!validateInput(activityInput.value)) {
    alert("Invalid input. Please use only letters, numbers, and spaces.");
    return;
  }
  try {
    window.socket.send(JSON.stringify({
      type: "create_activity_timer",
      activityName: activityInput.value,
      csrftoken: csrftoken
    }));
  } catch (e) {
    console.error('Error:', e);
  }
}


// Select quest
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
    window.socket.send(JSON.stringify({
      type: "choose_quest",
      quest_id: questId
    }));
  } catch (e) {
    console.error('Error:', e);
  }
}

function loadQuest(quest) {
  window.currentQuest = new Quest(quest.id, quest.name, quest.description, quest.intro_text, quest.outro_text, quest.duration, quest.stages);
  window.currentQuest.initialDisplay();
  window.questSelected = true;
  console.log("Quest loaded:", window.currentQuest);
  window.questTimer.startFromState(0, window.currentQuest.duration);
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
    window.socket.startTimers();
  }
}

// Submit an activity
async function submitActivity(event) {
  event.preventDefault();
  const activityInput = document.getElementById('activity-input');
  try {
    window.socket.send(JSON.stringify({
      type: "submit_activity",
      activityName: activityInput.value
    }));
  } catch (e) {
    console.error('There was a problem:', e);
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

// Submit quest
async function submitQuest() {
  try {
    window.socket.send(JSON.stringify({
      type: "quest_completed"
    }));
  } catch (e) {
    console.error('There was a problem:', e);
  }
}


// Fetch activities
async function fetchActivities() {
  try {
    window.socket.socket.send(JSON.stringify({
      type: "fetch_activities"
    }));
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

// Fetch eligible quests
async function fetchQuests() {
  try {
    window.socket.socket.send(JSON.stringify({
      type: "fetch_quests"
    }));
  } catch (e) {
    console.error('There was a problem:', e);
  }
}


// Fetch player & char info
async function fetchInfo() {
  try {
    window.socket.socket.send(JSON.stringify({
      type: "fetch_info"
    }));
  } catch (e) {
    console.error('There was a problem:', e);
  }
}


class ProfileWebSocket {
  constructor(profile_id) {
    this.profile_id = profile_id;
    this.socket = null;
  }

  connect() {
    this.socket = new WebSocket(`ws://${window.location.host}/ws/timers/profile_${this.profile_id}/`);

    this.socket.onopen = () => {
      console.log("Connected to timer socket");
    }

    this.socket.onmessage = (event) => {
      let data = JSON.parse(event.data);
      console.log("Received message:", data);
      handleSocketMessage(data);
    }

    this.socket.onerror = (error) => {
      console.error("Error:", error);
    }

    this.socket.onclose = (event) => {
      console.log("Socket closed:", event);
    }
  }

  startTimers() {
    this.socket.send(JSON.stringify({ type: "start_timers", action: "start_timers" }));
  }

  stopTimers() {
    this.socket.send(JSON.stringify({ type: "stop_timers", action: "stop_timers" }));
  }

  disconnect() {
    if (this.socket) {
      this.socket.stopTimers();
      this.socket.close();
    }
  }
}

function handleSocketMessage(data) {
  switch (data.type) {
    case "create_activity_timer_response":
      handleCreateActivityTimerResponse(data);
      break;
    case "choose_quest_response":
      handleChooseQuestResponse(data);
      break;
    case "submit_activity_response":
      handleSubmitActivityResponse(data);
      break;
    case "quest_completed_response":
      handleQuestCompletedResponse(data);
      break;
    case "fetch_activities_response":
      handleFetchActivitiesResponse(data);
      break;
    case "fetch_quests_response":
      handleFetchQuestsResponse(data);
      break;
    case "fetch_info_response":
      handleFetchInfoResponse(data);
      break;
    default:
      console.error("Unknown message type:", data.type);
  }
}

function handleCreateActivityTimerResponse(data) {
  if (data.success) {
    window.activitySelected = true;
    startTimerIfReady();
    document.getElementById('start-activity-btn').setAttribute("disabled", true);
    document.getElementById('activity-input-div').style.display = "none";
    document.getElementById('activity-name').innerText = data.activityName;
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
  } else {
    document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
  }
}

function handleSubmitActivityResponse(data) {
  if (data.success) {
    addActivityToList(data.activity);
    showInput();
    window.activityTimer.reset();
    window.activitySelected = false;
    document.getElementById('activity-status-text').innerText = "finished";
    document.getElementById('quest-status-text').innerText = "waiting";
  } else {
    console.error(data.message);
  }
}

function handleQuestCompletedResponse(data) {
  if (data.success) {
    submitQuestDisplayUpdate();
    window.questSelected = false;
    fetchQuests();
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
    const quests = data.quests;
    const questList = document.getElementById('quest-list-modal');
    questList.innerHTML = "";
    quests.forEach(quest => {
      const li = document.createElement("li");
      li.textContent = quest.name;
      li.dataset.index = quest.id;
      li.addEventListener("click", () => showQuestDetails(quest));
      questList.appendChild(li);
    });
  } else {
    console.error(data.message);
  }
}

function handleFetchInfoResponse(data) {
  if (data.success) {
    const character = data.character;
    const profile = data.profile;
    window.profile_id = profile.id;
    console.log("profile id:", window.profile_id);
    document.getElementById('player-name').innerText = profile.name;
    document.getElementById('player-xp').innerText = profile.xp;
    document.getElementById('player-xp-next').innerText = profile.xp_next_level;
    document.getElementById('player-level').innerText = profile.level;

    document.getElementById('character-name').innerText = character.name;
    document.getElementById('character-xp').innerText = character.xp;
    document.getElementById('character-xp-next').innerText = character.xp_next_level;
    document.getElementById('character-level').innerText = character.level;

    if (data.current_activity) {
      document.getElementById('activity-name').innerText = data.current_activity.name;
      //window.activityTimer.reset(elapsedTime = data.current_activity.duration);
      window.activitySelected = true;
      hideInput();
    }
    if (data.current_quest) {
      loadQuest(data.current_quest);
      //window.questTimer.reset(elapsedTime = data.current_quest.elapsed_time);
    }

    startTimerIfReady();
  } else {
    console.error(data.message);
  }
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

async function checkResponse(response) {
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response;
}

// Usage in an async function
async function fetchData(url) {
  const response = await fetch(url);
  await checkResponse(response);
  const data = await response.json();
  return data;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
