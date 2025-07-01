// hooks/useTimer.js
import { useState, useRef, useEffect, useCallback } from "react";

const loadFromServer = useCallback((serverData) => {
  if (!serverData) return;

  const { status, elapsed_time, duration, activity, quest } = serverData;

  setStatus(status || 'empty');
  setElapsed(elapsed_time || 0);

  if (mode === 'activity' && activity) {
    setSubject(activity); // assume you added `subject` via useState
    setDuration(elapsed_time); // or duration from the activity object if preferred
  }

  if (mode === 'quest' && quest) {
    setSubject(quest);
    setDuration(duration || 0);
  }
}, [mode]);

return {
  status,
  elapsed,
  duration,
  start,
  pause,
  reset,
  remainingTime: mode === "quest" ? Math.max(duration - elapsed, 0) : null,
  subject,
  setSubject,
  loadFromServer, // 👈 expose it
};

export default function useTimers({ mode, initialDuration = 0 }) {
  const [status, setStatus] = useState("empty"); // "empty", "active", "waiting", "completed"
  const [duration, setDuration] = useState(initialDuration); // total seconds for timer base
  const [elapsed, setElapsed] = useState(0); // seconds elapsed (activity) or elapsed for quest
  const [subject, setSubject] = useState(null); // the current activity or quest

  const intervalRef = useRef(null);
  const startTimeRef = useRef(null);
  const pausedTimeRef = useRef(0);

  // Timer tick handler — updates elapsed or remaining time
  const tick = useCallback(() => {
    const now = Date.now();
    const secondsPassed = Math.round((now - startTimeRef.current) / 1000);
    const newElapsed = pausedTimeRef.current + secondsPassed;

    if (mode === "quest") {
      const remaining = duration - newElapsed;
      if (remaining <= 0) {
        setElapsed(duration);
        setStatus("completed");
        clearInterval(intervalRef.current);
      } else {
        setElapsed(newElapsed);
      }
    } else {
      // activity mode counts elapsed up
      setElapsed(newElapsed);
    }
  }, [duration, mode]);

  // Start timer
  const start = useCallback(() => {
    if (status === "active") return;
    if (!subject) return;

    setStatus("active");
    startTimeRef.current = Date.now();
    pausedTimeRef.current = elapsed;
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(tick, 1000);
  }, [elapsed, status, tick]);

  // Pause timer
  const pause = useCallback(() => {
    if (status === "completed") return;
    if (!startTimeRef.current) return;

    const now = Date.now();
    const secondsPassed = Math.round((now - startTimeRef.current) / 1000);

    if (mode === "activity") {
      setDuration((prev) => prev + secondsPassed);
    } else if (mode === "quest") {
      setDuration((prev) => prev - secondsPassed);
    }

    setStatus("waiting");
    clearInterval(intervalRef.current);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
    setElapsed(0);
  }, [mode, status]);

  // Reset timer
  const reset = useCallback(() => {
    clearInterval(intervalRef.current);
    setStatus("empty");
    setElapsed(0);
    setDuration(0);
    setSubject(null);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
  }, []);

  // Assign subject to timer
  const assignSubject = useCallback((newSubject, newDuration = 0, newStatus = "waiting", newElapsed = 0) => {
    setSubject(newSubject);
    setStatus(newStatus);
    setElapsed(newElapsed);

    if (mode === "quest") {
      setDuration(newDuration);
    } else if (mode === "activity") {
      setDuration(0);
    }
  }, [mode]);

  // Cleanup on unmount
  useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);

  return {
    status,
    elapsed,
    duration,
    start,
    pause,
    reset,
    assignSubject,
    // For quest timer, expose remaining time for UI convenience
    remainingTime: mode === "quest" ? Math.max(duration - elapsed, 0) : null,
  };
}
