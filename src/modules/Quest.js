export class Quest {
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
    if (this.currentStageIndex < this.stages.length - 1) {
      this.renderPreviousStage();
      this.currentStageIndex++;
      document.getElementById("current-quest-active-stage").textContent =
        this.stages[this.currentStageIndex].text;
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
    stagesList.innerHTML += `<li>${
      this.stages[this.currentStageIndex].text
    }</li>`;
  }

  initialDisplay() {
    document.getElementById("current-quest-title").textContent = this.name;
    //document.getElementById('current-quest-description').textContent = this.description;
    document.getElementById("current-quest-intro").textContent = this.intro;
    document.getElementById("current-quest-active-stage").textContent =
      this.getCurrentStage().text;
    document.getElementById("current-quest-outro").textContent = this.outro;
  }

  resetDisplay() {
    const stagesList = document.getElementById("quest-stages-list");
    stagesList.style.display = "none";
    stagesList.innerHTML = "";
    document.getElementById("current-stage-section").style.display = "flex";
  }
}
