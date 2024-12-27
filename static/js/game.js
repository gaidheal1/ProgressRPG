document.addEventListener('DOMContentLoaded', () => {
  initialiseTimers();
  setupEventListeners();
  updateUI();
});
  

function initialiseTimers() {
  window.activityTimer = new Timer('activity-timer', mode="activity", duration=0);
  //window.activityTimer.stop();
  //console.log(window.activityTimer);
  window.questTimer = new Timer('quest-timer', mode="quest", duration=0);
  window.activitySelected = false;
  window.questSelected = false;
  
}
  
function setupEventListeners() {
  document.getElementById("start-activity-btn").addEventListener("click", createActivityTimer);
  document.getElementById("stop-activity-btn").addEventListener("click", submitActivity);
  document.getElementById('choose-quest-form').addEventListener('submit', chooseQuest);
  document.getElementById('show-rewards-btn').addEventListener('click', showRewards);
  document.getElementById('show-quests-btn').addEventListener('click', showQuests);
  
  // Timer event listeners
  window.activityTimer.on('stopped', onActivityTimerStopped);
  //window.activityTimer.on('completed', onActivityTimerCompleted);
  window.questTimer.on('stopped', onQuestTimerStopped);
  window.questTimer.on('completed', onQuestTimerCompleted)
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

class Quest {
  constructor(id, name, description, duration, stages, currentStageIndex = 0, elapsedTime = 0) {
    this.id = id;
    this.name = name;
    this.description = description;
    this.duration = duration;
    this.stages = stages;
    this.currentStageIndex = currentStageIndex;
    this.elapsedTime = elapsedTime;
  }

  getCurrentStage() {
    return this.stages[this.currentStageIndex];
  }

  advanceStage() {
    if (this.currentStageIndex < this.stages.length -1) {
      this.renderPreviousStage();
      this.currentStageIndex++;
      document.getElementById('quest-current-stage').textContent = this.stages[this.currentStageIndex].text;
    } else {
      console.log("Quest complete!");
    }
  }

  updateProgress(elapsedTime) {
    this.elapsedTime = elapsedTime;
    while (
      this.currentStageIndex < this.stages.length -1 &&
      this.elapsedTime >= this.stages[this.currentStageIndex].endTime
    ) {
      this.advanceStage();
    }
  }

  renderPreviousStage() {
    const stagesList = document.getElementById('quest-stages-list');
    if (stagesList.getAttribute('hidden')) {
      stagesList.removeAttribute('hidden');
    }
    stagesList.innerHTML += `<li>${this.stages[this.currentStageIndex].text}</li>`;
  }

  initialDisplay() {
    document.getElementById('quest-name').textContent = this.name;
    document.getElementById('quest-description').textContent = this.description;
    document.getElementById('quest-current-stage').textContent = this.stages[0].text;
  }

  resetDisplay() {
    const stagesList = document.getElementById('quest-stages-list');
    stagesList.setAttribute('hidden', true);
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
  off(event,  listener) {
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
    this.displayElement = document.getElementById(displayElementId); // Where to display the timer
    this.duration = duration; // Total time in seconds
    this.intervalId = null; // To track the interval
    this.startTime = new Date();
    this.elapsedTime = 0; // For countdown timers
    this.remainingTime = duration; // For countdown timers
    this.isRunning = false; // Timer state
    this.mode = mode;
  }

  start() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.intervalId = setInterval(() => {
      this.elapsedTime += 1;  
      if (this.mode === "quest") {
        this.remainingTime -= 1;
        //this.updateDisplay();

        window.currentQuest.updateProgress(this.elapsedTime)

        if (this.remainingTime <= 0) {
            this.stop();
            this.onComplete();
        }
      } //else if (this.mode === "activity") {
        
      this.updateDisplay();
    }, 1000);
  }
  
  stop() {
    if (!this.isRunning) return;
    console.log("timer stop function,", this.mode)
    this.isRunning = false;
    clearInterval(this.intervalId);
    this.emit('stopped', {timer: this});
  }

  reset(newDuration = this.duration) {
    this.stop();
    this.elapsedTime = 0;
    this.remainingTime = this.mode === "quest" ? newDuration : 0;
    this.updateDisplay();
    this.emit('reset', {timer: this});
  }

  updateDisplay() {
    let timeToDisplay = this.mode === "quest" ? this.remainingTime : this.elapsedTime;
    const minutes = Math.floor(timeToDisplay / 60);
    const seconds = timeToDisplay % 60;
    const text = `${minutes}:${seconds.toString().padStart(2, "0")}`
    this.displayElement.textContent = text;
  }

  onComplete() {
    console.log("Timer complete!");
    this.emit('completed', {timer: this});
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
  // Handle when the activity timer stops
  console.log("function onActivityTimerStopped");
  window.questTimer.stop();  // Stop the quest timer

}

function onQuestTimerStopped(data) {
  // Handle when the activity timer stops
  console.log("function onQuestTimerStopped!");
  window.activityTimer.stop();  // Stop the activity timer

}

function onQuestTimerCompleted(data) {
  // Handle when the quest timer completes
  console.log("function onQuestTimerCompleted");
  window.activityTimer.stop();  // Stop the activity timer
  submitQuest();
};

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  let formattedDuration = "";

  if (hours > 0) {
      formattedDuration += `${hours}:`;
  } 
  if (seconds > 0) {
      //if (formattedDuration) formattedDuration += " ";
      formattedDuration += `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  } else {
    formattedDuration = "00:00"
  }

  return formattedDuration;
}


// Start an activity timer
async function createActivityTimer() {
  try {
    const activityInput = document.getElementById('activity-input');
    const response = await fetch("/create_activity_timer/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value })
    })
    const data = await response.json();
    
    if (data.success) {
      window.activitySelected = true;
      //console.log('Activity ready')
      startTimerIfReady();
      document.getElementById('start-activity-btn').setAttribute("disabled", true);
      document.getElementById('stop-activity-btn').removeAttribute("disabled");
    }
  } catch(e) {
    console.error('Error:', e);
  };
}


// Select quest
async function chooseQuest(event) {
  event.preventDefault();
  if (window.currentQuest) {
    window.currentQuest.resetDisplay();
  }
  try {
    // Server url for choosing quest 
    const url = this.dataset.url;
    
    const quest = document.querySelector('input[name="quest"]:checked');
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({ "quest_id": quest.value })
    })
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    if (data.success) {
      window.currentQuest = new Quest(data.questId, data.questName, data.questDescription, data.questDuration, data.questStages);
      window.currentQuest.initialDisplay();
      window.questSelected = true;
      
      window.questTimer.reset(window.currentQuest.duration);
      document.getElementById('choose-quest').setAttribute("hidden", true);
      startTimerIfReady();
      quest.checked = false;
    } else { document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
    }
  } catch(e) {
      console.error('Error:', e);
  }
  
};


// Start timers when both activity and quest are selected
function startTimerIfReady() {
  if (window.activitySelected && window.questSelected) {
    
    // Start client timers
    window.activityTimer.start();  // Start the activity timer
    window.questTimer.start();     // Start the quest timer
    // Start server timers
    startActivityTimer();
    startQuestTimer();

    //console.log('Both timers started!');
  }
}



// Start an activity timer
async function startActivityTimer() {
  const response = await fetch("/start_activity_timer/", {method: "POST"});
  const data = await response.json()
}

// Stop an activity timer
async function stopActivityTimer() {
  activityTimer.stop()
  stopQuestTimer()
  const response = await fetch("/stop_activity_timer/", {method: "POST"});
  const data = await response.json();
}

// Start a quest timer
async function startQuestTimer() {
  const response = await fetch("/start_quest_timer/", {method: "POST"});
  const data = await response.json();
  //console.log("Remaining time:", data.remaining_time)
}

// Stop a quest timer
async function stopQuestTimer() {
  window.questTimer.stop()
  const response = await fetch("/stop_quest_timer/", {method: "POST"});
  const data = await response.json();
  //console.log("Elapsed time: ", data.elapsed_time);
}



// Submit an activity
async function submitActivity(event) {
  event.preventDefault();
  if (window.questSelected === true) {
    stopQuestTimer();
  }
  const activityInput = document.getElementById('activity-input');
  try {
    const response = await fetch("/submit_activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    addActivityToList(data.activities[0]);
    document.getElementById('start-activity-btn').removeAttribute("disabled");
    document.getElementById('stop-activity-btn').setAttribute("disabled", true);
    window.activityTimer.reset();
    window.activitySelected = false;
    activityInput.value = "";
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function addActivityToList(activity) {
  const activityList = document.getElementById('activity-list');
  const listItem = document.createElement('li');
  listItem.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
  activityList.prepend(listItem);
};




// Submit quest
async function submitQuest() {
  try {
    window.questTimer.stop()
    stopActivityTimer();
    const response = await fetch('/quest_completed/', {
      method: 'POST',
    });
    console.log('response ok:', response.ok);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    
    // Show rewards
    const rewardsList = document.getElementById('quest-rewards-list');
    console.log('quest xp reward:', data.xp_reward)
    rewardsList.innerHTML = `<li>${data.xp_reward} xp</li>`

    window.questSelected = false;
    document.getElementById('show-rewards-btn').removeAttribute("hidden");

    // Fetch updated list of eligible quests
    fetchQuests();

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
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    const activities = JSON.parse(data);
    const activityList = document.getElementById('activity-list');
    activityList.innerHTML = '';
    
    let activitiesNumber = 0;
    let activitiesTime = 0;
    activities.forEach(activity => {
      activitiesNumber += 1;
      activitiesTime += activity.duration;
      const li = document.createElement('li');
      li.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
      activityList.appendChild(li);
    });
    document.getElementById('activity-totals').innerText = `Total time today: ${formatDuration(activitiesTime)}; total activites today: ${activitiesNumber}`
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
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    const quests = JSON.parse(data);
    const questList = document.getElementById('quest-list');
    questList.innerHTML = '';

    quests.forEach(quest => {
      const li = document.createElement('li');
      li.innerHTML = `
        <label>
        <input type="radio", name="quest" value="${quest.id}" required>
        ${quest.name}
        </label><br>`;
      questList.appendChild(li);
    });
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
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const stuff = await response.json();
    data = JSON.parse(stuff);
    // Gotta check this is working when I can access websites again! :O
    console.log(data);
    const character = data.character;
    const profile = data.profile;
    document.getElementById('player-name').innerText = profile.name
    document.getElementById('player-xp').innerText = profile.xp
    document.getElementById('player-xp-next').innerText = data.profile_xp_next
    document.getElementById('player-level').innerText = profile.level

    document.getElementById('character-name').innerText = character.name
    document.getElementById('character-xp').innerText = character.xp
    document.getElementById('character-xp-next').innerText = data.character_xp_next
    document.getElementById('character-level').innerText = character.level
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function showRewards() {
  document.getElementById('show-rewards-btn').setAttribute("hidden", true);
  document.getElementById('quest-rewards').removeAttribute("hidden");
}

function showQuests() {
  document.getElementById('quest-rewards').setAttribute("hidden", true);
  document.getElementById('choose-quest').removeAttribute("hidden");
}

// Check state
async function checkTimers() {
  const response = await fetch("/get_timer_state/");
  const data = await response.json();
  //console.log("Activity Timer: ", data.activity_timer.elapsed_time);
  //console.log("Quest Timer: ", data.quest_timer.remaining_time);
}