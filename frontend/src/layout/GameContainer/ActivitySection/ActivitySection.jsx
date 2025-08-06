import React, { useState } from 'react';
import GameSection from '../GameSection';
import ActivityPanel from './ActivityPanel';
import { ActivityTimer } from '../../../components/Timer/ActivityTimer';

export default function ActivitySection() {

  return (
      <GameSection type="Activity">
        <ActivityTimer />
        <ActivityPanel />
      </GameSection>
  );
}
