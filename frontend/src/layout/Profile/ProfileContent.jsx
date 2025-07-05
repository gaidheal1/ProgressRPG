import React from 'react';

import styles from './ProfileContent.module.scss';

export default function GameContent() {

  return (
    <div className={styles.profileContent}>
      <div className={styles.profileSection}>
	<p>Player</p>
      </div>
      <div className={styles.profileSection}>
	<p>Character</p>
      </div>
    </div>
  );
}
