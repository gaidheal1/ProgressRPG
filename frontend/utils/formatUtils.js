
export function formatDuration(duration: number): string {
  const hours = Math.floor(duration / 3600);
  const mins = Math.floor((duration % 3600) / 60);
  const secs = duration % 60;

  const paddedMins = (hours > 0) ? String(mins).padStart(2, '0') : String(mins);
  const paddedSecs = String(secs).padStart(2, '0');

  return hours > 0
    ? `${hours}:${paddedMins}:${paddedSecs}`
    : `${paddedMins}:${paddedSecs}`;
}
