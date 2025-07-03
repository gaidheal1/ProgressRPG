import React, { useState, useEffect } from 'react';

export default function QuestPanel({ quest, onDurationChange }) {
  const [selectedDuration, setSelectedDuration] = useState(quest?.duration_options?.[0] || 60);

  useEffect(() => {
    // Reset duration when quest changes
    if (quest?.duration_options?.length) {
      setSelectedDuration(quest.duration_options[0]);
    }
  }, [quest]);

  const handleChange = (e) => {
    const newDuration = parseInt(e.target.value);
    setSelectedDuration(newDuration);
    onDurationChange?.(newDuration);
  };

  if (!quest) return <p>No quest selected yet.</p>;

  return (
    <div id="quest-panel" style={{ border: '1px solid #ccc', padding: '1rem' }}>
      <h2>{quest.name}</h2>
      <p>XP: {quest.xp}</p>

      <label htmlFor="duration-select">Select duration:</label>
      <select
        id="duration-select"
        value={selectedDuration}
        onChange={handleChange}
        style={{ marginLeft: '0.5rem' }}
      >
        {quest.duration_options.map((opt) => (
          <option key={opt} value={opt}>
            {opt} minutes
          </option>
        ))}
      </select>
    </div>
  );
}
