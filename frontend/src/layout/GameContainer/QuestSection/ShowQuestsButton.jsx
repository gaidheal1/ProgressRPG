import React from 'react';
import Button from '../../../components/Button/Button';

export default function ShowQuestsButton({ onClick }) {
  return (
    <div className="button-frame" id="show-quests-btn-frame">
      <Button className="button-filled" id="show-quests-btn" onClick={onClick}>
        Show quests
      </Button>
    </div>
  );
}
