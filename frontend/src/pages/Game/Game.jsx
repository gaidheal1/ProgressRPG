import React, { useState, useEffect } from 'react';
import ToastManager from '../../components/Toast/ToastManager';
import ProfileSocketListener from '../../components/ProfileSocketListener';
import { useGame } from '../../context/GameContext';
import styles from './Game.module.scss';
import GameContainer from '../../layout/GameContainer/GameContainer';

export default function Game() {
  const [toasts, setToasts] = useState([]);

  const { player, loading, error } = useGame();

  const showToast = (message) => {
    setToasts((prev) => [...prev, { id: Date.now(), message }]);
  };

  const handleWebSocketEvent = (data) => {
    switch (data.type) {
      case 'notification':
        showToast(data.message);
        break;
      case 'pong':
        console.log('[WS] Pong!');
        break;
      case 'console.log':
        console.log(data.message);
        break;
      case 'action':
        switch (data.action) {
          case 'start_timers':
            activityTimer.start();
            questTimer.start();
            break;
          case 'pause_timers':
            activityTimer.pause();
            questTimer.pause();
            break;
          case 'submit_activity':
            handleSubmitActivity();
            break;
          case 'quest_complete':
            handleCompleteQuest();
            break;
          default:
            console.warn('[WS] Unknown action:', data);
        }
        break;
      default:
        console.warn('[WS] Unknown type:', data);
    }
  };

  if (loading) return <p>Loading game data...</p>;
  if (error) return <p>Error: {error}. Please refresh the page!</p>;

  return (
    <div className={styles.gamePage}>
      {player?.id && <ProfileSocketListener onEvent={handleWebSocketEvent} />}
      <ToastManager messages={toasts} />

      <GameContainer
        showToast={showToast}
      />
    </div>
  );
}
