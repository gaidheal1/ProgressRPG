document.addEventListener('DOMContentLoaded', () => {
    const activityTimerDisplay = document.getElementById('activity-timer');
    const questTimerDisplay = document.getElementById('quest-timer');
    const activityInput = document.getElementById('activity-input');
    const startButton = document.getElementById('start-activity-btn');
    const stopButton = document.getElementById('stop-activity-btn');
    let activityTimer = 0;
    let questTimer = parseInt(questTimerDisplay.textContent); // Example quest time
  
    let activityInterval, questInterval;
  
    startButton.addEventListener('click', () => {
      createActivityTimer(activityInput);

      activityInterval = setInterval(() => {
        activityTimer++;
        activityTimerDisplay.textContent = new Date(activityTimer * 1000).toISOString().substr(11, 8);
      }, 1000);
  
      if (!questInterval) {
        questInterval = setInterval(() => {
          if (questTimer > 0) {
            questTimer--;
            questTimerDisplay.textContent = new Date(questTimer * 1000).toISOString().substr(11, 8);
          } else {
            clearInterval(questInterval);
            //alert('Quest Completed!');
          }
        }, 1000);
      }
    });
  
    stopButton.addEventListener('click', () => {
      stopActivityTimer();
      stopQuestTimer();
      clearInterval(activityInterval);
      clearInterval(questInterval);
    });

    document.getElementById('choose-quest-form').addEventListener('submit', function(event) {
      event.preventDefault();
      
      const questId = document.querySelector('input[name="quest"]:checked').value;
      fetch("{% url 'choose_quest' %}", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
          },
          body: JSON.stringify({ "quest_id": questID })
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              document.getElementById('feedback-message').textContent = "Quest selection successful!";
              // Can also immediately update UI to show current quest
              document.getElementById('quest-name').textContent = "{{ character.current_quest.name }}";
              document.getElementById('quest-description').textContent = "{{ character.current_quest.description }}";
              document.getElementById('quest-timer').textContent = "{{ character.quest_timer.get_remaining_time() }}";
          } else { document.getElementById('feedback-message').textContent = "Quest selection failed, please try again.";
          }
      })
      .catch(error => {
          console.error('Error:', error);
          document.getElementById('feedback-message').textContent = An error occurred. Please try again.";
      });
    });
  });
  


  // Start an activity timer
  async function createActivityTimer(activityInput) {
    await fetch("/gameplay/create-activity-timer/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
  }

// Start an activity timer
  async function startActivityTimer() {
    const response = await fetch("/gameplay/start-activity-timer/", {method: "POST"});
    const data = await response.json()
  }

  // Stop an activity timer
  async function stopActivityTimer() {
    const response = await fetch("/gameplay/stop-activity-timer/", {method: "POST"});
    const data = await response.json();
    console.log("Elapsed time: ", data.elapsed_time);
  }

 // Submit an activity
  async function submitActivity(activityInput) {
    await fetch("/gameplay/submit-activity/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ activityName: activityInput.value }),
    });
  }

// Start a quest timer
  async function startQuestTimer() {
    const response = await fetch("/gameplay/start-quest-timer/", {method: "POST"});
    const data = await response.json();
    //console.log("Remaining time:", data.remaining_time)
  }

  // Stop a quest timer
  async function stopQuestTimer() {
    const response = await fetch("/gameplay/stop-quest-timer/", {method: "POST"});
    const data = await response.json();
    //console.log("Elapsed time: ", data.elapsed_time);
  }

  // Check state
  async function checkTimers() {
    const response = await fetch("/gameplay/get-timer-state/");
    const data = await response.json();
    console.log("Activity Timer: ", data.activity_timer.elapsed_time);
    console.log("Quest Timer: ", data.quest_timer.remaining_time);
  }