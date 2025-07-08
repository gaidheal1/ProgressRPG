// hooks/useTimer.js
import { useState, useRef, useEffect, useCallback } from "react";
import { apiFetch } from "../../utils/api.js";

export default function useTimers({ mode }) {
  const [id, setId] = useState(0);
  const [status, setStatus] = useState("empty"); // "empty", "active", "waiting", "completed"
  const [duration, setDuration] = useState(0); // total seconds for timer base
  const [elapsed, setElapsed] = useState(0); // seconds elapsed (activity) or elapsed for quest
  const [subject, setSubject] = useState(null); // the current activity or quest
  const [stages, setStages] = useState([]);

  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [stageTimeRemaining, setStageTimeRemaining] = useState(
    stages[0]?.duration ?? stages[0]?.endTime ?? 0
  );

  const timerRef = useRef(null);
  const stageTimerRef = useRef(null);
  const startTimeRef = useRef(null);
  const pausedTimeRef = useRef(0);

  // Timer tick handler — updates elapsed or remaining time
  const tick = useCallback(() => {
    const now = Date.now();
    const secondsPassed = Math.round((now - startTimeRef.current) / 1000);
    const newElapsed = pausedTimeRef.current + secondsPassed;
    
    setElapsed(newElapsed);
    
    if (mode === "quest") {
      const remaining = duration - newElapsed;
      if (remaining <= 0) {
        setElapsed(duration);
        complete();
      }

      const stageRemaining = stages[currentStageIndex].duration - (stageTimeRemaining + secondsPassed);
      console.log('New stageRemaining:', stageRemaining);
      setStageTimeRemaining(stageRemaining);
      if (stageRemaining <=0) {
        setCurrentStageIndex(currentStageIndex + 1);
      }
    }
  }, [duration, mode]);

  // Start timer
  const start = useCallback(() => {
    if (status === "active") return;
    if (!subject) return;
    console.log(`[useTimers] Start ${mode}`);
    const data = apiFetch(`/${mode}_timers/${id}/start/`, {
      method: 'POST',
    });
    setStatus("active");
    startTimeRef.current = Date.now();
    pausedTimeRef.current = elapsed;
    clearInterval(timerRef.current);
    timerRef.current = setInterval(tick, 1000);
    
    clearInterval(stageTimerRef.current);
    stageTimerRef.current = setInterval(tick, stageTimeRemaining);

  }, [elapsed, status, tick]);

  // Pause timer
  const pause = useCallback(() => {
    if (
      status === "paused" ||
      status === "waiting"
    ) return;
    if (!startTimeRef.current) return;

    console.log(`[useTimers] Pause ${mode}`);
    const data = apiFetch(`/${mode}_timers/${id}/pause/`, {
      method: 'POST',
    });
    const now = Date.now();
    const secondsPassed = Math.round((now - startTimeRef.current) / 1000);

    if (mode === "activity") {
      setDuration((prev) => prev + secondsPassed);
    } else if (mode === "quest") {
      setDuration((prev) => prev - secondsPassed);
    }

    setStatus("waiting");
    clearInterval(timerRef.current);
    clearInterval(stageTimerRef);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
    //setElapsed(0);
  }, [mode, status]);


  // Complete timer
  const complete = useCallback(() => {
    console.log(`[useTimers] Complete ${mode}`);
    if (status === "complete") return;
    clearInterval(timerRef.current);
    clearInterval(stageTimerRef.current);
    setStatus("complete");
  }, []);

  // Reset timer
  const reset = useCallback(() => {
    if (status === "empty") return;
    console.log(`[useTimers] Reset ${mode}`);
    const data = apiFetch(`/${mode}_timers/${id}/reset/`, {
      method: 'POST',
    });
    setDuration(0);
    setSubject(null);
    setStatus("empty");
    setElapsed(0);
    startTimeRef.current = null;
    pausedTimeRef.current = 0;
  }, []);

  // Assign subject to timer
  const assignSubject = useCallback((newSubject, newDuration = 0, newStatus = "waiting", newElapsed = 0) => {
    console.log(`[useTimers] Assign ${mode}`);
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
    return () => clearInterval(timerRef.current);
  }, []);


  const loadFromServer = useCallback((serverData) => {
    if (!serverData) return;

    const { id, status, elapsed_time, duration, activity, quest } = serverData;
    console.log('quest.stages:', quest.stages);
    //setStages(quest.stages || []);

    setId(id || 0);
    setStatus(status || 'empty');
    setElapsed(elapsed_time || 0);

    if (mode === 'activity' && activity) {
      setSubject(activity);
      setDuration(elapsed_time);
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
    subject,
    remainingTime: mode === "quest" ? Math.max(duration - elapsed, 0) : null,
    start,
    pause,
    complete,
    reset,
    assignSubject,
    loadFromServer,
  };
}
