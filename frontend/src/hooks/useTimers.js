// hooks/useTimer.js
import { useState, useRef, useEffect, useCallback } from "react";

export default function useTimers({ mode }) {
  const [status, setStatus] = useState("empty"); // "empty", "active", "waiting", "completed"
  const [duration, setDuration] = useState(0); // total seconds for timer base
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
        complete();

      } else {
        setElapsed(newElapsed);
      }
    } else {
      // activity mode counts elapsed up
      setElapsed(newElapsed);
      console.log("Tick, newElapsed:", newElapsed);
    }
    console.log("Tick, elapsed:", elapsed);
  }, [duration, mode]);

  // Start timer
  const start = useCallback(() => {
    if (status === "active") return;
    if (!subject) return;
    console.log('[useTimers] Start')
    setStatus("active");
    startTimeRef.current = Date.now();
    pausedTimeRef.current = elapsed;
    console.log('pausedTimeRef:', pausedTimeRef);
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(tick, 1000);
  }, [elapsed, status, tick]);

  // Pause timer
  const pause = useCallback(() => {
    if (
      status === "paused" ||
      status === "waiting"
    ) return;

    if (!startTimeRef.current) return;
    console.log(`[useTimers] Pause ${mode}`);

    const now = Date.now();
    const secondsPassed = Math.round((now - startTimeRef.current) / 1000);

    if (mode === "activity") {
      console.log('Activity elapsed before:', elapsed);
      console.log('Seconds passed:', secondsPassed);
      setDuration((prev) => prev + secondsPassed);
    } else if (mode === "quest") {
      setDuration((prev) => prev - secondsPassed);
    }

    setStatus("waiting");
    clearInterval(intervalRef.current);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
    //setElapsed(0);
  }, [mode, status]);


  // Complete timer
  const complete = useCallback(() => {
    console.log(`[useTimers] Complete ${mode}`);
    if (status === "complete") return;
    clearInterval(intervalRef.current);
    setStatus("complete");
  }, []);

  // Reset timer
  const reset = useCallback(() => {
    console.log(`[useTimers] Reset ${mode}`);
    setDuration(0);
    setSubject(null);
    setStatus("empty");
    setElapsed(0);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
  }, []);

  // Assign subject to timer
  const assignSubject = useCallback((newSubject, newDuration = 0, newStatus = "waiting", newElapsed = 0) => {
    console.log('[useTimers] Assign subject')
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

  const loadFromServer = useCallback((serverData) => {
    if (!serverData) return;

    const { status, elapsed_time, duration, activity, quest } = serverData;

    setStatus(status || 'empty');
    setElapsed(elapsed_time || 0);

    if (mode === 'activity' && activity) {
      setSubject(activity);
      setDuration(elapsed_time); // or activity.duration if preferred
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
    complete,
    reset,
    assignSubject,
    remainingTime: mode === "quest" ? Math.max(duration - elapsed, 0) : null,
    loadFromServer,
  };
}
