import { chooseQuest, completeQuest } from '../api/questApi.js';
import { loadQuestList, showQuestDetails } from '../handlers/uiHandlers.js';
import { Quest } from '../modules/Quest.js'

export function onQuestCompleted(data) {
  ws.pauseTimers();
  window.activityTimer.pause();
  completeQuest();
}

export function loadQuest(quest_timer) {
  console.log("[LOAD QUEST]");
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
  window.questTimer.setup(
    quest_timer.status,
    quest_timer.elapsed_time,
    quest_timer.duration
  );
}

export function loadQuestList(quests) {
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