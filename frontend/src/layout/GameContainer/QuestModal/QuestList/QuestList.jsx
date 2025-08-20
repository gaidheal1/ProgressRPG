import React, { useState } from 'react';
import styles from './QuestList.module.scss';
import List from '../../../../components/List/List';

export default function QuestList({ quests, selectedQuest, onSelect }) {
  const [selected, setSelected] = useState(null);

  return (
    <div className={styles.questList}>
      <List
        items={quests}
        selectable
        selectedItem={selectedQuest}
        onSelect={onSelect}
        getItemKey={(quest) => quest.id ?? quest.name}
        renderItem={(quest, isSelected) => (
          <>
            {quest.name}
          </>
        )}
      />
    </div>

  );
}

// EXAMPLE USAGE
/*


export default function FruitList() {
  const [selected, setSelected] = React.useState(null);

  return (
    <List
      items={items}
      selectable
      selectedItem={selected}
      onSelect={setSelected}
      renderItem={(item) => <span>{item}</span>}
    />
  );
}

 */
