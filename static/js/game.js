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
        if (this.mode === "quest") {
            this.remainingTime -= 1;
            this.updateDisplay();

            if (this.remainingTime <= 0) {
                this.stop();
                this.onComplete();
            }
        } else if (this.mode === "activity") {
            this.elapsedTime += 1;
            this.updateDisplay();
        }
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
  //stopActivityTimer();
  //stopQuestTimer();
}

function onQuestTimerStopped(data) {
  // Handle when the activity timer stops
  console.log("function onQuestTimerStopped!");
  window.activityTimer.stop();  // Stop the activity timer
  //stopActivityTimer();
  //stopQuestTimer();
}

function onQuestTimerCompleted(data) {
  // Handle when the quest timer completes
  console.log("function onQuestTimerCompleted");
  window.activityTimer.stop();  // Stop the activity timer
  submitQuest();
};


// Select quest
function chooseQuest(event) {
  event.preventDefault();
  const url = this.dataset.url;
  
  const quest = document.querySelector('input[name="quest"]:checked');
  fetch(url, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
      },
      body: JSON.stringify({ "quest_id": quest.value })
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          //console.log(data)
          window.questSelected = true;
          document.getElementById('feedback-message').textContent = "Quest selection successful!";
          // Can also immediately update UI to show current quest
          document.getElementById('quest-name').textContent = data.questName;
          document.getElementById('quest-description').textContent = data.questDescription;
          
          window.questTimer.reset(data.questDuration)
          document.getElementById('choose-quest').setAttribute("hidden", true);
          startTimerIfReady();
      } else { document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
      }
  })
  .catch(e => {
      console.error('Error:', e);
      document.getElementById('feedback-message').textContent = "An error occurred. Please try again.";
  });
  quest.checked = false;
};


// Start an activity timer
async function createActivityTimer() {
  const activityInput = document.getElementById('activity-input');
  await fetch("/create_activity_timer/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ activityName: activityInput.value })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.activitySelected = true;
      //console.log('Activity ready')
      startTimerIfReady();
      console.log("test response:", data.activity_id);
      document.getElementById('start-activity-btn').setAttribute("disabled", true);
    }
  })
  .catch(e => {
    console.error('Error:', e);
  });
}


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
  
  //console.log("Elapsed time: ", data.elapsed_time);
}

// Submit an activity
async function submitActivity(event) {
  event.preventDefault();
  stopQuestTimer();
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
    window.activityTimer.reset();
    activityInput.value = "";
  } catch (e) {
    console.error('There was a problem:', e);
  }
}

function addActivityToList(activity) {
  const activityList = document.getElementById('activity-list');
  const listItem = document.createElement('li');
  listItem.textContent = `${activity.name} - duration ${activity.duration}`;
  activityList.prepend(listItem);
};


// Start a quest timer
async function startQuestTimer() {
  const response = await fetch("/start_quest_timer/", {method: "POST"});
  const data = await response.json();
  //console.log("Remaining time:", data.remaining_time)
}

// Stop a quest timer
async function stopQuestTimer() {
  questTimer.stop()
  const response = await fetch("/stop_quest_timer/", {method: "POST"});
  const data = await response.json();
  //console.log("Elapsed time: ", data.elapsed_time);
}

// Submit quest
async function submitQuest() {
  questTimer.stop()
  stopActivityTimer();
  fetch('/quest_completed/', {
    method: 'POST',
  });
  questSelected = false;
  document.getElementById('choose-quest').removeAttribute("hidden");
}

// Check state
async function checkTimers() {
  const response = await fetch("/get_timer_state/");
  const data = await response.json();
  //console.log("Activity Timer: ", data.activity_timer.elapsed_time);
  //console.log("Quest Timer: ", data.quest_timer.remaining_time);
}