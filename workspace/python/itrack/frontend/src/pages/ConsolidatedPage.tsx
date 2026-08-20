import React from 'react';
import { ConsolidatedDashboard } from '../components/ConsolidatedDashboard';
import { SettingsProvider } from '../contexts/SettingsContext';

export const ConsolidatedPage: React.FC = () => {
  return (
    <SettingsProvider>
      <ConsolidatedDashboard />
    </SettingsProvider>
  );
};
