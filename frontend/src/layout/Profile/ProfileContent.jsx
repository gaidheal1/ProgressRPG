import React from 'react';
import styles from './ProfileContent.module.scss';
import FeatureToggle from '../../components/FeatureToggle';
import ActivityList from '../ActivityList/ActivityList';

export default function ProfileContent(props) {

  return (
    <div className={styles.profileContent}>
      <div className={styles.profileSection}>
	      <h1>Player</h1>
        <FeatureToggle flag="activityList">
          <ActivityList {...props} />
        </FeatureToggle>
      </div>
      <div className={styles.profileSection}>
	      <h1>Character</h1>
      </div>
    </div>
  );
}
