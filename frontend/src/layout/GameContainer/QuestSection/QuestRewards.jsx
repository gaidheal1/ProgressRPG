import React from 'react';
import List from '../../../components/List/List';
import styles from './QuestRewards.module.scss';

export default function QuestRewards({ rewards = {}, visible = false }) {
  const { xp = 0, coins = 0, other = [] } = rewards;

  if (!visible) return null;

  // Prepare items to render in the list
  const items = [
    { id: 'xp', label: 'XP', value: xp },
    { id: 'coins', label: 'Coins', value: coins },
    ...other.map((item, i) => ({ id: `other-${i}`, label: item })),
  ];

  // Custom renderItem to show label and value or just label
  const renderItem = (item) => {
    if ('value' in item) {
      return (
        <>
          <span>{item.label}:</span>
          <span>{item.value}</span>
        </>
      );
    }
    return item.label;
  };

  return (
    <div className={`${styles.container} listSection`}>
      <h2 className={styles.header}>Quest rewards</h2>
      <List
        items={items}
        renderItem={renderItem}
      />
    </div>
  );
}
