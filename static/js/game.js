document.addEventListener('DOMContentLoaded', () => {
    const activityTimerDisplay = document.getElementById('activity-timer');
    const questTimerDisplay = document.getElementById('quest-timer');
    const startButton = document.getElementById('start-activity-btn');
    const stopButton = document.getElementById('stop-activity-btn');
    let activityTimer = 0;
    let questTimer = parseInt(questTimerDisplay.textContent); // Example quest time
  
    let activityInterval, questInterval;
  
    startButton.addEventListener('click', () => {
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
            alert('Quest Completed!');
          }
        }, 1000);
      }
    });
  
    stopButton.addEventListener('click', () => {
      clearInterval(activityInterval);
    });
  });
  