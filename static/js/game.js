document.addEventListener('DOMContentLoaded', () => {
  initialiseTimers();
  setupEventListeners();
  updateUI();
});
  

function initialiseTimers() {
  window.activityTimer = new Timer('activity-timer', mode="activity", duration=0);
  window.questTimer = new Timer('quest-timer', mode="quest", duration=0);
  window.activitySelected = false;
  window.questSelected = false;
}
  
function setupEventListeners() {
  document.getElementById("start-activity-btn").addEventListener("click", createActivityTimer);
  document.getElementById('choose-quest-form').addEventListener('submit', chooseQuest);
  document.getElementById('show-quests-btn').addEventListener('click', showQuests);
  
  const stopButton = document.getElementById("stop-activity-btn");
  stopButton.addEventListener("click", submitActivity);
  stopButton.style.display = "none";

  // Timer event listeners
  window.activityTimer.on('stopped', onActivityTimerStopped);
  //window.activityTimer.on('completed', onActivityTimerCompleted);
  window.questTimer.on('stopped', onQuestTimerStopped);
  window.questTimer.on('completed', onQuestTimerCompleted); 
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
    if (stagesList.style.display == "none") {
      stagesList.style.display == "flex";
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
    stagesList.style.display == "none";
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
    this.intervalIdTime = null; // To track the interval
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
        window.currentQuest.updateProgress(this.elapsedTime)

        if (this.remainingTime <= 0) {
            this.stop();
            this.onComplete();
        }
      };
      this.updateDisplay();
    }, 1000);
    // Start sync timer
    this.intervalIdSync = setInterval(() => {
      this.elapsedTime = syncTimer(this.mode);
    }, 3000); // 300000 for 5 minutes, smaller for testing
  }
  
  stop() {
    if (!this.isRunning) return;
    console.log("timer stop function,", this.mode)
    this.isRunning = false;
    clearInterval(this.intervalIdTime);
    this.emit('stopped', {timer: this});
    clearInterval(this.intervalIdSync)
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
  event.preventDefault();
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
      startTimerIfReady();
      
      document.getElementById('start-activity-btn').setAttribute("disabled", true);
      document.getElementById('activity-input-div').style.display = "none";
      
      document.getElementById('activity-name').innerText = activityInput.value;

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
    
    const selectedQuest = document.querySelector('input[name="quest"]:checked');
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({ "quest_id": selectedQuest.value })
    })
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    if (data.success) {
      document.getElementById('quest-rewards').style.display = "none";
      const quest = data.quest;
      window.currentQuest = new Quest(quest.id, quest.name, quest.description, quest.duration, quest.stages);
      window.currentQuest.initialDisplay();
      window.questSelected = true;
      
      window.questTimer.reset(window.currentQuest.duration);
      document.getElementById('choose-quest').style.display = "none";
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

    // Change activity buttons
    document.getElementById('start-activity-btn').style.display = "none";
    document.getElementById('stop-activity-btn').style.display = "flex";
    document.getElementById('stop-activity-btn').removeAttribute("disabled");
    // Update statuses
    document.getElementById('activity-status-text').innerText = "running";
    document.getElementById('quest-status-text').innerText = "running";

    // Start client timers
    window.activityTimer.start();  // Start the activity timer
    window.questTimer.start();     // Start the quest timer
    // Start server timers
    startTimer("activity");
    startTimer("quest");

    //console.log('Both timers started!');
  }
}



// Start an activity timer
async function startTimer(mode) {
  try {
    const response = await fetch("/start_timer/", {
        method: 'POST',
        headers: {"Content-Type": "text/plain"},
        body: mode,
      });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    const data = await response.json();
    if (data.success) {
      console.log(data.message)
    } else {
      console.error(data.messsage)
    }
  } catch (e) {
    console.error('There was a problem:', e);
  };
};

// Stop an activity timer
async function stopTimer(mode) {
  try {
    activityTimer.stop()
    const response = await fetch("/stop_timer/", {
        method: 'POST',
        headers: {"Content-Type": "text/plain"},
        body: mode,
      });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (data.success) {
      console.log(data.message)
    } else {
      console.error(data.messsage)
    }
  } catch (e) {
    console.error('There was a problem:', e);
  };
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
    if (data.success) {
      console.log(data.message)
      const activityList = document.getElementById('activity-list');
      if (activityList.innerText == "") {
        console.log("No activities today.. so far");
      }
      addActivityToList(data.activities[0]);
      // Adjust display
      document.getElementById('start-activity-btn').removeAttribute("disabled");
      document.getElementById('stop-activity-btn').setAttribute("disabled", true);
      activityInput.style.display = "flex";

      window.activityTimer.reset();
      window.activitySelected = false;
      // Update statuses
      document.getElementById('activity-status-text').innerText = "finished";
      document.getElementById('quest-status-text').innerText = "waiting";

      activityInput.value = "";
    } else {
      console.error(data.messsage)
    }
    
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function addActivityToList(activity) {
  const activityList = document.getElementById('activity-list');
  const listItem = document.createElement('li');
  const activitiesTimeMessage = document.getElementById('activities-time-message');
  // Add activity as list item
  listItem.textContent = `${activity.name} - ${formatDuration(activity.duration)}`;
  activityList.prepend(listItem);
  
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
    if (data.success) {
      console.log(data.message)
      // Show rewards
      const rewardsList = document.getElementById('quest-rewards-list');
      console.log('quest xp reward:', data.xp_reward)
      rewardsList.innerHTML = `<li>${data.xp_reward} xp</li>`
      document.getElementById('quest-rewards').style.display = "flex";
      document.getElementById('show-quests-btn-frame').style.display = "flex";
      window.questSelected = false;
      
      // Update statuses
      document.getElementById('activity-status-text').innerText = "waiting";
      document.getElementById('quest-status-text').innerText = "finished";
      
      // Fetch updated list of eligible quests
      fetchQuests();
    } else {
      console.error(data.messsage)
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
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (data.success) {
      console.log(data.message)
      const activities = data.activities;
      const activityList = document.getElementById('activity-list');
      activityList.innerHTML = '';
      window.activitiesNumber = 0;
      window.activitiesTime = 0;
      if (activities.length == 0) {
        document.getElementById('activity-totals').innerText = "No activities done today!"
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
          activityTimeMessage.innerText = "Total time today: "
          document.getElementById('activities-total-message').innerText = "; total activities today: "
        };
        document.getElementById('activities-time-data').innerText = formatDuration(window.activitiesTime);
        document.getElementById('activities-total-data').innerText = window.activitiesNumber;
      }
    } else {
      console.error(data.messsage)
    }
    
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
    if (data.success) {
      const quests = data.quests;
      const questList = document.getElementById('quest-list');
      questList.innerHTML = '';

      if (quests.length == 0) {
        questList.innerText = "No quests available, sorry!";
      } else {
        quests.forEach(quest => {
          const li = document.createElement('li');
          li.innerHTML = `
            <label>
            <input type="radio", name="quest" value="${quest.id}" required>
            ${quest.name}
            </label><br>`;
          questList.appendChild(li);
        });
      };
    } else {
      console.error(data.message)
    }
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
    const data = await response.json();
    if (data.success) {
      const character = data.character;
      const profile = data.profile;
      document.getElementById('player-name').innerText = profile.name
      document.getElementById('player-xp').innerText = profile.xp
      document.getElementById('player-xp-next').innerText = profile.xp_next_level
      document.getElementById('player-level').innerText = profile.level

      document.getElementById('character-name').innerText = character.name
      document.getElementById('character-xp').innerText = character.xp
      document.getElementById('character-xp-next').innerText = character.xp_next_level
      document.getElementById('character-level').innerText = character.level
    } else {
      console.error(data.message)
    }
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function showQuests() {
  document.getElementById('show-quests-btn-frame').style.display = "none";
  document.getElementById('choose-quest').style.display = "flex";
}

// Check state
async function syncTimer(mode) {
    console.log("timer mode:", mode)
    try {
    const response = await fetch("/get_timer_state/", {
      method: 'POST',
      headers: {"Content-Type": "text/plain"},
      body: mode,
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    if (data.success) {
      console.log("syncTimer data response:", data);
      if (mode == "activity") {
        return data.timer.elapsed_time  
      } else if (mode == "quest") {
        return data.timer.remaining_time;
      }
    } else {
      console.error(data.message)
    }
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

