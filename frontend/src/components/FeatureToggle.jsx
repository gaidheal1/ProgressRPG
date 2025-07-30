// src/components/FeatureToggle.jsx
import React from 'react';
import featureFlags from '../featureFlags';

export default function FeatureToggle({ flag, children, fallback }) {
  // Check if the flag is enabled in the passed featureFlags object
  const isEnabled = featureFlags[flag];

  // Default fallback message if none is passed
  const defaultFallback = <p>This feature is coming soon! Stay tuned.</p>;

  return isEnabled ? children : (fallback ?? defaultFallback);
}
