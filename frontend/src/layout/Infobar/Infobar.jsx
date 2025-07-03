import React from 'react';
import { useGame } from '../../context/GameContext';
import Infobox from './Infobox/Infobox';
import styles from './Infobar.module.scss';

export default function Infobar() {
  const { player, character } = useGame();

  if (!player || !character) return null;

  return (
    <div className={styles.infoBar}>
      <Infobox
        title={player.name}
        columns={[
          [
            { label: 'Player', value: player.name },
            { label: 'Level', value: player.level },
            { label: 'XP', value: `${player.xp}/${player.xp_next_level}` },
          ],
        ]}
      />
      <Infobox
        title={character.first_name}
        columns={[
          [
            { label: 'Character', value: character.first_name },
            { label: 'Level', value: character.level },
            { label: 'XP', value: `${character.xp}/${character.xp_next_level}` },
          ],
        ]}
      />
    </div>
  );
}
