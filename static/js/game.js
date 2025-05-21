function openModal() {
  window.modal.style.display = "block";
}

function closeModal() {
  window.modal.style.display = "none";
}

function showToast(message) {
  console.log("showToast called with message:", message);
  const toastContainer = document.getElementById("toast-container");
  console.log("Toast container:", toastContainer);
  const toast = document.createElement("div");
  toast.classList.add("toast");
  toast.textContent = message;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3300);
}

function showQuestDetails(quest) {
  const dropdown = document.getElementById("quest-durations");
  console.log("quest durations:", quest.duration_choices);
  dropdown.innerHTML = "";
  quest.duration_choices.forEach((choice) => {
    let durationText = "";
    if (choice >= 60) {
      durationText = `${Math.round(choice / 60)} minutes`;
    } else {
      durationText = `${choice} seconds`;
    }
    const option = document.createElement("option");
    option.value = choice;
    option.textContent = durationText;
    dropdown.appendChild(option);
  });
  document.getElementById("quest-title").textContent = quest.name;
  document.getElementById("quest-description").textContent = quest.description;
  //document.getElementById('xp-reward-value').textContent = quest.result.xp_reward;
  //document.getElementById('coin-reward-value').textContent = quest.result.coin_reward;
  //const otherRewards = document.getElementById('other-rewards-list');
  //otherRewards.innerHTML = "";
  //Object.entries(quest.result.dynamic_rewards).forEach(([key, value]) => {
  //  const li = document.createElement("li");
  //  li.textContent = `${key}: ${value}`;
  //  otherRewards.appendChild(li);
  //});
  document
    .querySelectorAll("#quest-list-modal li")
    .forEach((li) => li.classList.remove("selected"));
  document
    .querySelector(`li[data-index="${quest.id}"]`)
    .classList.add("selected");
}

class Quest {
  constructor(
    id,
    name,
    description,
    intro,
    outro,
    stages,
    currentStageIndex = 0,
    elapsedTime = 0
  ) {
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
    const stagesList = document.getElementById("quest-stages-list");

    if (this.currentStageIndex < this.stages.length - 1) {
      this.renderPreviousStage();
      this.currentStageIndex++;
      document.getElementById("current-quest-active-stage").textContent =
        this.stages[this.currentStageIndex].text;

      const existingCurrent = stagesList.querySelector(".quest-stage.current");
      if (existingCurrent) {
        existingCurrent.classList.remove("current");
        existingCurrent.classList.add("previous");
      }

      const li = document.createElement("li");
      li.textContent = this.stages[this.currentStageIndex].text;
      li.classList.add("quest-stage", "current");
      stagesList.appendChild(li);
    } else {
      console.log("Quest complete!");
    }
  }

  updateProgress(elapsedTime) {
    while (
      this.currentStageIndex < this.stages.length - 1 &&
      elapsedTime >= this.stages[this.currentStageIndex].endTime
    ) {
      this.advanceStage();
    }
  }

  renderPreviousStage() {
    const stagesList = document.getElementById("quest-stages-list");
    if (stagesList.style.display == "none") {
      stagesList.style.display = "flex";
    }
    const prevStage = this.stages[this.currentStageIndex];
    const li = document.createElement("li");
    li.textContent = prevStage.text;
    li.classList.add("quest-stage", "previous")
    stagesList.appendChild(li);
  }

  initialDisplay() {
    document.getElementById("current-quest-title").textContent = this.name;
    document.getElementById("current-quest-intro").textContent = this.intro;
    document.getElementById("current-quest-outro").textContent = this.outro;
    
    const stagesList = document.getElementById("quest-stages-list");
    stagesList.style.display = "flex";

    const li = document.createElement("li");
    li.textContent = this.getCurrentStage().text;
    li.classList.add("quest-stage", "current");
    stagesList.appendChild(li);
  }

  resetDisplay() {
    const stagesList = document.getElementById("quest-stages-list");
    if (stagesList) {
      stagesList.style.display = "none";
      stagesList.innerHTML = "";
    }

    const currentStageSection = document.getElementById("current-stage-section");
    if (currentStageSection) {
      currentStageSection.style.display = "flex";
    }
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
    this.events[event] = this.events[event].filter((l) => l !== listener);
  }

  // Emit
  emit(event, data) {
    if (!this.events[event]) return;
    this.events[event].forEach((listener) => listener(data));
  }
}

class Timer extends EventEmitter {
  constructor(displayElementId, mode, status = "empty", duration = 0) {
    super();
    this.displayElement = document.getElementById(displayElementId);
    this.statusElement = document.getElementById(`${mode}-status-text`);
    this.status = status;
    this.duration = duration;
    this.intervalIdTime = null;
    //this.startTime = None;
    this.elapsedTime = 0; // For countdown timers
    this.remainingTime = duration; // For countdown timers
    this.mode = mode;
  }

  setup(timer) {
    this.reset();
    this.startTime = timer.start_time;
    if (this.mode === "activity") {
      this.duration = timer.elapsed_time;
      this.elapsedTime = this.duration;
    } else if (this.mode === "quest") {
      this.duration = timer.remaining_time;
      this.remainingTime = this.duration;
    }
    this.updateStatus(timer.status);
    this.updateDisplay();
  }

  start() {
    console.log(`${this.mode} timer start method. Status: ${this.status}`);
    if (this.status === "completed") return;
    this.updateStatus("active");
    // Start timer
    this.startTime = Date.now();
    this.intervalIdTime = setInterval(() => this.updateTimer(), 1000);
  }

  pause() {
    const elapsedTime = Math.round((Date.now() - this.startTime) / 1000);
    // console.log(
    //   `$[TIMER.PAUSE] ${this.mode} timer before. Status: ${this.status}, duration: ${this.duration}, elapsedTime: ${elapsedTime}`
    // );
    if (this.status === "completed") return;
    this.updateStatus("waiting");
    if (this.mode === "activity") {
      this.duration += elapsedTime;
    } else if (this.mode === "quest") {
      this.duration -= elapsedTime;
    }
    this.startTime = null;
    // console.log(
    //   `$[TIMER.PAUSE] ${this.mode} timer after. Duration: ${this.duration}`
    // );
    clearInterval(this.intervalIdTime);
    this.emit("paused", { timer: this });
  }

  reset() {
    this.updateStatus("empty");
    this.elapsedTime = 0;
    this.duration = 0;
    this.startTime = null;
    if (this.mode === "quest") {
      this.remainingTime = 0;
    }
    this.emit("reset", { timer: this });
    this.updateDisplay();
  }

  updateStatus(status) {
    console.log(`${this.mode} timer update status, status: ${status}`);
    this.status = status;
    this.statusElement.innerText = status;
  }

  updateTimer() {
    const elapsedTime = Math.round((Date.now() - this.startTime) / 1000);
    if (this.mode === "activity") {
      this.elapsedTime = this.duration + elapsedTime;
      // console
      //   .log(
      //   `[TIMER.UPDATE TIMER] ${this.mode} timer. this.elapsedTime: ${this.elapsedTime}, duration: ${this.duration}, elapsedTime: ${elapsedTime}`
      //   );
    } else if (this.mode === "quest") {
      this.remainingTime = this.duration - elapsedTime;
      // console.log(
      //   `[TIMER.UPDATE TIMER] ${this.mode} timer. this.remainingTime: ${this.remainingTime}, duration: ${this.duration}, elapsedTime: ${elapsedTime}`
      //);
      window.currentQuest.updateProgress(this.remainingTime);
      if (this.remainingTime <= 0) {
        this.remainingTime = 0;
        this.onComplete();
      }
    }
    console.log();
    this.updateDisplay();
  }

  updateDisplay() {
    const timeToDisplay =
      this.mode === "quest" ? this.remainingTime : this.elapsedTime;
    const hours = Math.floor(timeToDisplay / 3600);
    const minutes = Math.floor((timeToDisplay % 3600) / 60);
    const seconds = timeToDisplay % 60;
    if (hours > 0) {
      this.displayElement.textContent = `${hours}:${minutes
        .toString()
        .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    } else {
      this.displayElement.textContent = `${minutes}:${seconds
        .toString()
        .padStart(2, "0")}`;
    }
  }

  onComplete() {
    this.pause();
    console.log("Timer complete!");
    this.updateStatus("completed");
    this.emit("completed", { timer: this });
  }
}

// activityHandlers.js
function onActivitySubmitted(data) {
  window.ws.submitActivity();
  //window.questTimer.pause();
  pauseTimers();
}

// questHandlers.js
function onQuestCompleted(data) {
  console.log("[ON QUEST COMPLETED]");
  window.activityTimer.pause();
  window.ws.completeQuest();
}

// format.js
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours > 0 ? `${hours}:` : ""}${minutes
    .toString()
    .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

// questHandlers.js
function loadQuest(quest_timer) {
  //console.log("[LOAD QUEST]");
  const quest = quest_timer.quest;
  //const duration = data.duration;
  window.currentQuest = new Quest(
    quest.id,
    quest.name,
    quest.description,
    quest.intro_text,
    quest.outro_text,
    quest.stages
  );
  window.currentQuest.initialDisplay();
  window.questSelected = true;
  window.questTimer.setup(quest_timer);
}

// timerHandlers.js
function startTimers() {
  // Double-check that timers are ready
  // if (
  //   window.activityTimer.status in ["paused", "waiting", "ready"] &&
  //   window.questTimer.status in ["paused", "waiting", "ready"]
  // ) {
  // Change buttons
  document.getElementById("start-activity-btn").style.display = "none";
  document.getElementById("stop-activity-btn").style.display = "flex";
  document.getElementById("stop-activity-btn").removeAttribute("disabled");
  document.getElementById("show-quests-btn-frame").style.display = "none";
  // Start timers
  window.activityTimer.start();
  window.questTimer.start();
  // } else {
  //   console.error(
  //     `Timers not ready to start. Timers status: ${window.activityTimer.status}/${window.questTimer.status}`
  //   );
  // }
}

// timerHandlers.js
function pauseTimers() {
  // Change buttons

  // Pause timers
  if (window.activityTimer.status === "active") {
    window.activityTimer.pause();
  }
  if (window.questTimer.status === "active") {
    window.questTimer.pause();
  }
}

// activityHandlers.js
function addActivityToList(activity) {
  const activityList = document.getElementById("activity-list");
  const listItem = document.createElement("li");
  // Can't read .name???
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

// domUtils.js
function submitQuestDisplayUpdate() {
  // Change buttons
  document.getElementById("quest-rewards").style.display = "flex";
  document.getElementById("show-quests-btn-frame").style.display = "flex";
  // Reset quest modal details pane
  document.getElementById("quest-title").textContent = "No quest selected";
  document.getElementById("quest-description").textContent = "";
  document.getElementById("xp-reward-value").textContent = "";
  document.getElementById("coin-reward-value").textContent = "";
  document.getElementById("other-rewards-list").innerHTML = "";
  // Display outro message
  document.getElementById("current-quest-outro").style.display = "flex";
}

// questHandlers.js
function loadQuestList(quests) {
  const questList = document.getElementById("quest-list-modal");
  questList.innerHTML = "";
  quests.forEach((quest) => {
    const li = document.createElement("li");
    li.textContent = quest.name;
    li.dataset.index = quest.id;
    li.addEventListener("click", () => showQuestDetails(quest));
    questList.appendChild(li);
  });
}

// domUtils.js
function updatePlayerInfo(profile) {
  document.getElementById("player-name").innerText = profile.name;
  document.getElementById("player-xp").innerText = profile.xp;
  document.getElementById("player-xp-next").innerText = profile.xp_next_level;
  document.getElementById("player-level").innerText = profile.level;
}

// domUtils.js
function updateCharacterInfo(character) {
  document.getElementById("character-name").innerText = character.name;
  document.getElementById("character-xp").innerText = character.xp;
  document.getElementById("character-xp-next").innerText =
    character.xp_next_level;
  document.getElementById("character-level").innerText = character.level;
}

// domUtils.js
function showStartHideStop() {
  const startActivityButton = document.getElementById("start-activity-btn");
  startActivityButton.removeAttribute("disabled");
  startActivityButton.style.display = "flex";
  const stopActivityButton = document.getElementById("stop-activity-btn");
  stopActivityButton.setAttribute("disabled", true);
  stopActivityButton.style.display = "none";
}

// domUtils.js
function hideStartShowStop() {
  const startActivityButton = document.getElementById("start-activity-btn");
  startActivityButton.setAttribute("disabled", true);
  startActivityButton.style.display = "none";
  const stopActivityButton = document.getElementById("stop-activity-btn");
  stopActivityButton.removeAttribute("disabled");
  stopActivityButton.style.display = "flex";
}

// domUtils.js
function showQuests() {
  document.getElementById("show-quests-btn-frame").style.display = "none";
}

// format.js
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// validate.js
function validateInput(input) {
  const pattern = /^[a-zA-Z0-9\s]+$/; // Adjust pattern as needed
  return pattern.test(input);
}

///////////////////////////
// AJAX REQUEST FUNCTIONS
///////////////////////////

// api/activityApi.js
async function createActivity() {
  const activityInput = document.getElementById("activity-input");
  // if (!validateInput(activityInput.value)) {
  //   alert("Invalid input. Please use only letters, numbers, and spaces.");
  //   return;
  // }
  try {
    const response = await fetch("/create_activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
    const data = await response.json();
    handleCreateActivityResponse(data);
  } catch (e) {
    console.error("Error:", e);
  }
}

// api/activityApi.js
async function submitActivity(event) {
  const activityInput = document.getElementById("activity-input");

  // let activity;
  // if (localStorage.getItem("pendingActivity")) {
  //   activity = JSON.parse(localStorage.getItem("pendingActivity"));
  // } else {
  //   activity = {
  //     name: activityInput.value,
  //   };
  // }

  let activity = {
    name: activityInput.value,
  };
  console.log(`[SUBMIT ACTIVITY] Activity: ${activity}`);

  try {
    const response = await fetch("/submit_activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(activity),
    });
    await checkResponse(response);
    const data = await response.json();

    handleSubmitActivityResponse(data);
    //localStorage.removeItem("pendingActivity");
  } catch (e) {
    console.error("There was a problem submitting the activity:", e);
    //localStorage.setItem("pendingActivity", JSON.stringify(activityData));
    // console.warn(
    //   "Activity submission failed. It will be retried when you're reconnected."
    // );
  }
}

// api/questApi.js
async function chooseQuest(event) {
  event.preventDefault();
  if (window.currentQuest) {
    window.currentQuest.resetDisplay();
  }
  try {
    const selectedQuest = document.querySelector("#quest-list-modal .selected");
    if (!selectedQuest) {
      alert("Please select a quest first.");
      return;
    }
    const questId = selectedQuest.dataset.index;
    const selectedDuration = document.getElementById("quest-durations");
    console.log(
      `[CHOOSE QUEST] questId: ${questId}, duration: ${selectedDuration.value}`
    );
    if (!selectedDuration) {
      alert("Please select a duration for your quest.");
      return;
    }
    const response = await fetch("/choose_quest/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        quest_id: questId,
        duration: selectedDuration.value,
      }),
    });
    await checkResponse(response);

    const data = await response.json();
    handleChooseQuestResponse(data);
  } catch (e) {
    console.error("Error:", e);
  }
}

// api/questApi.js
async function completeQuest() {
  try {
    const response = await fetch("/complete_quest/", {
      method: "POST",
    });

    await checkResponse(response);
    const data = await response.json();
    handleQuestCompleteResponse(data);

    localStorage.removeItem("pendingQuest");
  } catch (e) {
    if (e instanceof TypeError) {
      console.error("Network error:", e.message);
    } else {
      console.error("API error:", e.message);
    }

    //localStorage.setItem("pendingQuest", JSON.stringify(true));
    console.warn(
      "Quest completion failed. It will be retried when you're reconnected."
    );
  }
}

// api/activityApi.js
async function fetchActivities() {
  try {
    const response = await fetch("/fetch_activities/", {
      method: "GET",
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchActivitiesResponse(data);
  } catch (e) {
    console.error("There was a problem:", e);
  }
}

// api/questApi.js
async function fetchQuests() {
  try {
    const response = await fetch("/fetch_quests/", {
      method: "GET",
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchQuestsResponse(data);
  } catch (e) {
    console.error("There was a problem:", e);
  }
}

// Fetch player & char info
async function fetchInfo() {
  try {
    const response = await fetch("/fetch_info/", {
      method: "GET",
    });
    await checkResponse(response);
    const data = await response.json();
    handleFetchInfoResponse(data);
  } catch (e) {
    console.error("There was a problem:", e);
  }
}

//////////////////////////////////////////////
// RESPONSE HANDLER FUNCTIONS ////////////////
//////////////////////////////////////////////

function handleCreateActivityResponse(data) {
  if (data.success) {
    window.activitySelected = true;
    window.activityTimer.updateStatus("waiting");
    document
      .getElementById("start-activity-btn")
      .setAttribute("disabled", true);
    if (window.questSelected === true) {
      window.ws.createActivity();
    }
  } else {
    console.error(data.message);
  }
}

function handleUpdateActivityNameResponse(data) {
  if (data.success) {
    //console.log("Activity name updated:", data.new_name);
  } else {
    console.error(data.message);
  }
}

function handleSubmitActivityResponse(data) {
  if (data.success) {
    console.log(
      "[HANDLE SUBMIT ACTIVITY] First activity in list:",
      data.activities[0]
    );
    addActivityToList(data.activities[0]);
    document.getElementById("activity-input").value = "";
    showStartHideStop();
    window.activityTimer.reset();
    window.activitySelected = false;

    updatePlayerInfo(data.profile);

    if (window.questTimer.status !== "completed") {
      window.questTimer.updateStatus("waiting");
    }
  } else {
    console.error(data.message);
  }
}

function handleChooseQuestResponse(data) {
  if (data.success) {
    // Reset quest display
    document.getElementById("quest-rewards").style.display = "none";
    document.getElementById("current-quest-outro").style.display = "none";

    loadQuest(data.quest_timer);
    closeModal();
    //window.activityTimer.updateStatus("waiting");
    window.ws.chooseQuest();
  } else {
    document.getElementById("feedback-message").textContent =
      "Quest selection failed, please try again.";
  }
}

function handleQuestCompleteResponse(data) {
  if (data.success) {
    console.log(
      `[QUEST COMPLETE RESPONSE] Server timer status: ${data.activity_timer_status}/${data.quest_timer_status}`
    );
    submitQuestDisplayUpdate();
    window.questSelected = false;
    if (window.currentQuest) {
      window.currentQuest.renderPreviousStage();
    }
    document.getElementById("current-stage-section").style.display = "none";
    // document
    //   .getElementById("start-activity-btn")
    //   .setAttribute("disabled", true);
    updateCharacterInfo(data.character);
    loadQuestList(data.quests);
  } else {
    console.error(data.message);
  }
}

function handleFetchActivitiesResponse(data) {
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
      li.textContent = `${activity.name} - ${formatDuration(
        activity.duration
      )}`;
      activityList.appendChild(li);
    });

    const activityTimeMessage = document.getElementById(
      "activities-time-message"
    );
    if (activityTimeMessage.innerText == "") {
      activityTimeMessage.innerText = "Total time today: ";
      document.getElementById("activities-total-message").innerText =
        "; total activities today: ";
    }
    document.getElementById("activities-time-data").innerText = formatDuration(
      window.activitiesTime
    );
    document.getElementById("activities-total-data").innerText =
      window.activitiesNumber;
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
    //window.profile_id = data.profile.id;
    updatePlayerInfo(data.profile);
    updateCharacterInfo(data.character);

    const activity_timer = data.activity_timer;
    //console.log("Data:", data);
    console.log("[HANDLE FETCH INFO] Activity timer:", activity_timer);

    window.activityTimer.setup(activity_timer);

    if (activity_timer.status !== "empty" && activity_timer.activity) {
      window.activitySelected = true;
      document.getElementById("activity-input").value =
        activity_timer.activity.name;
      hideStartShowStop();
    }

    const quest_timer = data.quest_timer;
    console.log("[HANDLE FETCH INFO] Quest timer:", quest_timer);

    if (quest_timer.status !== "empty") {
      loadQuest(quest_timer);
    } else {
      console.log("[HANDLE FETCH INFO] Quest timer status is empty.");
    }

    if (window.ws) {
      window.ws.startTimers();
    }
  } else {
    console.error(data.message);
  }
}

async function checkResponse(response) {
  if (!response.ok) {
    const errorMessage = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorMessage}`);
  }
  return response;
}

////////////////////////////////
/////// WEBSOCKETS       //////
//////////////////////////////

class ProfileWebSocket {
  constructor(profile_id) {
    this.profile_id = profile_id;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    return new Promise((resolve, reject) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        console.log("Already connected to the WebSocket.");
        return resolve(); // Immediately resolve as the connection is already established
      }

      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${protocol}://${window.location.host}/ws/profile_${this.profile_id}/`;

      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log("Connected to timer socket");
        resolve();
        this.startPing();

        //if (
        //  window.activityTimer.status in ["paused", "waiting", "ready"] &&
        //  window.questTimer.status in ["paused", "waiting", "ready"]
        //) {
        //  this.startTimers();
        //}
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        let data;
        try {
          data = JSON.parse(event.data);
          console.log("Received message:", data);
          handleSocketMessage(data);
        } catch (e) {
          console.error("Error parsing JSON:", e, event.data);
        }
      };

      this.socket.onerror = (error) => {
        console.error("WebSocket Error:", error);

        (async () => {
          try {
            await submitBugReport({ message: "WebSocket error", error });
          } catch (reportError) {
            console.error("Bug report submission failed:", reportError);
          }
        })();
      };

      this.socket.onclose = (event) => {
        console.log("Socket closed:", event);
        this.stopPing();
        pauseTimers();
        this.reconnect();
      };
    });
  }

  startTimers() {
    this.send({
      type: "client_request",
      action: "start_timers",
    });
  }

  pauseTimers() {
    console.log("WS attempting to pause timers...");
    this.send({
      type: "client_request",
      action: "pause_timers",
    });
  }

  createActivity() {
    console.log("WS attempting to create activity...");
    this.send({
      type: "client_request",
      action: "create_activity",
    });
  }

  chooseQuest() {
    console.log("WS attempting to choose quest...");
    this.send({
      type: "client_request",
      action: "choose_quest",
    });
  }

  submitActivity() {
    console.log("WS attempting to submit activity...");
    this.send({
      type: "client_request",
      action: "submit_activity",
    });
  }

  completeQuest() {
    console.log("WS attempting to complete quest...");
    this.send({
      type: "client_request",
      action: "complete_quest",
    });
  }

  get readyState() {
    return this.socket.readyState;
  }

  send(data) {
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log("Websocket sending message:", data);
        this.socket.send(JSON.stringify(data));
      } else {
        console.error("Socket not open, cannot send message");
      }
    } else {
      console.error("Websocket not initialised.");
    }
  }

  startPing() {
    this.pingInterval = setInterval(() => {
      if (this.socket.readyState === WebSocket.OPEN) {
        //console.log("Sending ping...");
        this.send({ type: "ping" });
      }
    }, 10000);
  }

  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      alert("Max reconnect attempts reached. Stopping retries.");
      return;
    }

    let timeout = Math.min(5000, 1000 * 3 ** this.reconnectAttempts);
    console.log(`Reconnecting in ${timeout / 1000} seconds...`);

    setTimeout(() => {
      if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
        this.socket.close(); // Close the existing connection if open
      }

      this.reconnectAttempts++;

      this.connect();
      this.socket.onopen = () => {
        console.log("Reconnected to timer socket");
        handleReconnect();
      };
    }, timeout);
  }
}

function handleSocketMessage(data) {
  if (data.action) {
    //console.log(`Data action: ${data.action}`);
    switch (data.action) {
      case "start_timers":
        console.log("Received start timers command");
        handleStartTimersResponse(data);
        break;
      case "pause_timers":
        console.log("Received pause timers command");
        handlePauseTimersResponse(data);
        break;
      case "correct_quest_timer":
        console.log("Received correct timer command");
        handleCorrectTimerResponse(data);
        break;
      case "create_activity":
        console.log("Received create activity notification");
        startTimers();
        break;
      case "choose_quest":
        console.log("Received choose quest notification");
        startTimers();
        break;
      case "submit_activity":
        console.log("Received submity activity notification");
        submitActivity(data);
        break;
      case "quest_complete":
        console.log("Received quest complete notification");
        completeQuest();
        break;
      case "pong":
        handlePong(data);
        break;
      case "console.log":
        console.log(data.message);
        break;
      case "warn":
        console.error(data.message);
        break;
      case "notification":
        showToast(data.message);
        break;
      default:
        console.error("Unknown message action:", data.action);
    }
  } else {
    console.error("Expected data.action, got none. Data:", data);
  }
}

function handleStartTimersResponse(data) {
  if (data.success) {
    console.log(`[HANDLE STARTTIMERS RESPONSE] ${data}`);
    startTimers();
  } else {
    console.error(`[HANDLE STARTTIMERS RESPONSE] Checking data: ${data}`);
  }
}

function handlePauseTimersResponse(data) {
  if (data.success) {
    console.log(`[HANDLE PAUSETIMERS RESPONSE] ${data}`);
    pauseTimers();
  } else {
    console.error(`[HANDLE PAUSETIMERS RESPONSE] Checking data: ${data}`);
  }
}

function handleCorrectTimerResponse(data) {
  if (data.success) {
    console.log(`[HANDLE CORRECTQUESTTIMERS RESPONSE] ${data}`);
    window.questTimer.setup(data.data);
    startTimers();
  } else {
    console.error(
      `[HANDLE CORRECTQUESTTIMERS RESPONSE] Checking data: ${data}`
    );
  }
}

// Function to handle reconnection logic and retry any pending data
function handleReconnect() {
  const pendingActivity = localStorage.getItem("pendingActivity");
  if (pendingActivity) {
    console.log("Found pending activity, attempting to resubmit...");
    submitActivity();
  }
  const pendingQuest = localStorage.getItem("pendingQuest");
  if (pendingQuest) {
    console.log("Found pending quest, attempting to resubmit...");
    //await completeQuest();
  }
}

function handlePong(data) {
  //console.log(data.message);
}

////////////////////////////////////////////////////////////////
/////// INITIALISE APP   //////////////////////////////////////
//////////////////////////////////////////////////////////////

document.addEventListener("DOMContentLoaded", () => {
  initialiseTimers();
  setupEventListeners();
  connectWebsocket();
  updateUI();
});

function initialiseTimers() {
  window.activityTimer = new Timer("activity-timer", "activity", 0);
  window.questTimer = new Timer("quest-timer", "quest", 0);
  window.activitySelected = false;
  window.questSelected = false;
}

function setupEventListeners() {
  document
    .getElementById("start-activity-btn")
    .addEventListener("click", createActivity);
  document
    .getElementById("stop-activity-btn")
    .addEventListener("click", onActivitySubmitted);
  document
    .getElementById("show-quests-btn")
    .addEventListener("click", openModal);
  document
    .getElementById("close-modal-btn")
    .addEventListener("click", closeModal);
  document.getElementById("quest-modal").addEventListener("click", (e) => {
    if (e.target === window.modal) closeModal();
  });
  document
    .getElementById("choose-quest-btn")
    .addEventListener("click", chooseQuest);
  window.questTimer.on("completed", onQuestCompleted);

  // Capture global errors
  window.onerror = function (message, source, lineno, colno, error) {
    console.error("Global error captured:", {
      message,
      source,
      lineno,
      colno,
      error,
    });
    submitBugReport({ message, source, lineno, colno, error });
  };

  // Capture unhandled promise rejections
  window.onunhandledrejection = function (event) {
    console.error("Unhandled promise rejection:", event.reason);
    submitBugReport({
      message: "Unhandled promise rejection",
      error: event.reason,
    });
  };

  // WebSocket error handling
  //  window.ws.onerror = function (error) {
  //    console.error("WebSocket error occurred:", error);
  //    submitBugReport({ message: "WebSocket error", error });
  //};
}

function connectWebsocket() {
  // Initialise WebSocket

  const gameplayContainer = document.getElementById("gameplay-container");
  const profileId = gameplayContainer?.dataset.profileId;
  window.DEBUG = gameplayContainer?.dataset.debug;
  window.DEBUG = window.DEBUG.toLowerCase() === "true" ? true : false;
  //console.log(`profileId: ${profileId}`);
  console.log(`debug: ${window.DEBUG}`);

  if (profileId) {
    window.ws = new ProfileWebSocket(profileId);
    window.ws.connect();
  } else {
    console.error("Profile ID not found. WebSocket not initialised.");
  }
}

function updateUI() {
  window.modal = document.getElementById("quest-modal");
  fetchActivities();
  fetchQuests();
  fetchInfo();
}

window.addEventListener("offline", () => {
  console.log("User is now offline.");
});

let isQuestRetrying = false;

window.addEventListener("online", async () => {
  console.log("User is back online. Attempting to submit pending reports...");
  const connection = await checkInternetConnection();
  if (connection) {
    await submitPendingReports();
    if (localStorage.getItem("pendingQuest") && !isQuestRetrying) {
      isQuestRetrying = true;
      console.log("Retrying quest completion...");
      await completeQuest();
      isQuestRetrying = false;
    }
  }
});

async function checkInternetConnection() {
  if (!navigator.onLine) {
    console.warn("Client is offline based on navigator.onLine");
    return false;
  }

  try {
    const response = await fetch("/static/js/ping.json", { cache: "no-store" });

    if (response.ok) {
      console.log("Internet connection verified.");
      return true;
    } else {
      console.error(
        "Failed to fetch the resource. Response status:",
        response.status
      );
      return false;
    }
  } catch (e) {
    console.error("Error during connectivity check:", e);
    return false;
  }
}

function saveBugReportLocally(errorDetails) {
  const reports = JSON.parse(localStorage.getItem("bugReports")) || [];
  reports.push({
    timestamp: new Date().toISOString(),
    error: errorDetails,
  });
  localStorage.setItem("bugReports", JSON.stringify(reports));
}

async function submitPendingReports() {
  try {
    const reports = JSON.parse(localStorage.getItem("bugReports")) || [];
    for (const report of reports) {
      await submitBugReport(report);
    }
  } catch (e) {
    console.error("There was a problem submitting pending reports:", e);
  }
}

async function submitBugReport(errorDetails) {
  try {
    const connectionOk = await checkInternetConnection();
    if (!connectionOk) {
      saveBugReportLocally(errorDetails);
      return;
    }
  } catch (e) {
    console.error("Error while checking connection:", e);
    saveBugReportLocally(errorDetails);
    return;
  }
  try {
    const response = await fetch("/submit_bug_report/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        error: errorDetails,
      }),
    });
    await checkResponse(response);
    const data = await response.json();
    handleSubmitBugReportResponse(data, errorDetails);
  } catch (e) {
    console.error("There was a problem submitting bug report:", e);
    saveBugReportLocally(errorDetails);
  }
}

function handleSubmitBugReportResponse(data, submittedReport) {
  if (data.success) {
    console.log("Pending bug report submitted successfully.");
    // Remove submitted report from local storage
    const remainingReports = JSON.parse(
      localStorage.getItem("bugReports")
    ).filter((r) => r.timestamp !== submittedReport.timestamp);
    localStorage.setItem("bugReports", JSON.stringify(remainingReports));
  } else {
    console.error("Error submitting report:", data.message);
  }
}

function logMessage(level, message, ...optionalParams) {
  if (window.DEBUG) {
    // Dev mode: Log to the console
    switch (level) {
      case "error":
        console.error(message, ...optionalParams);
        break;
      case "warn":
        console.warn(message, ...optionalParams);
        break;
      case "info":
        console.info(message, ...optionalParams);
        break;
      default:
        console.log(message, ...optionalParams);
    }
  } else {
    // Prod mode: Send logs to a server (or ignore non-errors)
    if (level === "error" || level === "warn") {
      fetch("/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level, message, details: optionalParams }),
      });
    }
  }
}
