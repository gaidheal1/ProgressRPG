import React from 'react';
import { useGame } from '../../context/GameContext';
import Infobox from './Infobox/Infobox';
import styles from './Infobar.module.scss';

export default function Infobar() {
  const { player, character, loading } = useGame();
  console.log("[INFOBAR] Player, character:", player, character);


  if (loading) return <div className={styles.infoBar}>Loading data...</div>;
  if (!player || !character) {
  return <div className={styles.infoBar}>Loading player/character info...</div>;
  }

  return (
    <div className={styles.infoBar}>
      <Infobox title="Player Info" type="player" data={player} />
      <Infobox title="Character Info" type="character" data={character} />
    </div>
  );
}
