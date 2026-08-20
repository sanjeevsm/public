import React from 'react';
import { LiabilityManagement } from '../components/LiabilityManagement';
import { SettingsProvider } from '../contexts/SettingsContext';

export const LiabilityPage: React.FC = () => {
  return (
    <SettingsProvider>
      <LiabilityManagement />
    </SettingsProvider>
  );
};
