import React from 'react';
import { useGame } from '../../context/GameContext';
import Infobox from './Infobox/Infobox';
import styles from './Infobar.module.scss';

export default function Infobar() {
  const { player, character } = useGame();

  if (!player || !character) return null;

  return (
    <div className={styles.infoBar}>
      <Infobox title="Player Info" type="player" data={player} />
      <Infobox title="Character Info" type="character" data={character} />
    </div>
  );
}
