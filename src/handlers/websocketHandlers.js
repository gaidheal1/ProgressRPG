
export function handleStartTimersResponse(data) {
  if (data.success) {
    console.log(data.message);
    startTimers();
  } else {
    console.error(data.message);
  }
}

export function handlePauseTimersResponse(data) {
  if (data.success) {
    console.log(data.message);
    pauseTimers();
  } else {
    console.error(data.message);
  }
}

export function handlePong(data) {
  console.log(data.message);