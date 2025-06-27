import { formatDuration } from './format.js'

export function showInput() {
  const startActivityButton = document.getElementById("start-activity-btn");
  startActivityButton.removeAttribute("disabled");
  startActivityButton.style.display = "flex";
  const stopActivityButton = document.getElementById("stop-activity-btn");
  stopActivityButton.setAttribute("disabled", true);
  stopActivityButton.style.display = "none";
  document.getElementById("activity-input-div").style.display = "flex";
}

export function hideInput() {
  const startActivityButton = document.getElementById("start-activity-btn");
  startActivityButton.setAttribute("disabled", true);
  startActivityButton.style.display = "none";
  const stopActivityButton = document.getElementById("stop-activity-btn");
  stopActivityButton.removeAttribute("disabled");
  stopActivityButton.style.display = "flex";
}

export function updatePlayerInfo(profile) {
  document.getElementById("player-name").innerText = profile.name;
  document.getElementById("player-xp").innerText = profile.xp;
  document.getElementById("player-xp-next").innerText = profile.xp_next_level;
  document.getElementById("player-level").innerText = profile.level;
}

export function updateCharacterInfo(character) {
  document.getElementById("character-name").innerText = character.name;
  document.getElementById("character-xp").innerText = character.xp;
  document.getElementById("character-xp-next").innerText =
    character.xp_next_level;
  document.getElementById("character-level").innerText = character.level;
}

export function showQuestDetails(quest) {
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

export function submitQuestDisplayUpdate() {
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

export function showQuests() {
  document.getElementById("show-quests-btn-frame").style.display = "none";
}
