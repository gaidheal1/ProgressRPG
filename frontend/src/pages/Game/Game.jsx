// pages/Game/Game.jsx
import React, { useState, useEffect } from 'react';

import { useGame } from '../../context/GameContext';
import { useWebSocket } from '../../context/WebSocketContext';
import { useWebSocketEvent } from '../../hooks/useWebSocketEvent';

import styles from './Game.module.scss';
import GameContainer from '../../layout/GameContainer/GameContainer';

function handleWebSocketEvent(data, { showToast, activityTimer, questTimer }) {
    //console.log("New WS data:", data);
    if (data.type !== 'action') return;

    switch (data.action) {
      case 'start_timers':
        //activityTimer.start();
        //questTimer.start();
        break;
      case 'pause_timers':
        //activityTimer.pause();
        //questTimer.pause();
        break;
      case 'submit_activity':
        //handleSubmitActivity();
        console.log("Server WS sent 'submit_activity'");
        break;
      case 'quest_complete':
        //handleCompleteQuest();
        console.log("Server WS sent 'complete_quest'");
        break;
      default:
        console.warn('[WS] Unknown action:', data);
    }
}

export default function Game() {
  const { player, activityTimer, questTimer, loading, showToast, error } = useGame();
  const { addEventHandler } = useWebSocket();

  useWebSocketEvent((data) => {
    handleWebSocketEvent(data, { showToast, activityTimer, questTimer })
  });


  if (loading) return <p>Loading game data...</p>;
  if (error) return <p>Error: {error}. Please refresh the page!</p>;

  return (
    <div className={styles.gamePage}>
      <GameContainer />
    </div>
  );
}
