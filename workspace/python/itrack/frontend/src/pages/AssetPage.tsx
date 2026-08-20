import React from 'react';
import { AssetManagement } from '../components/AssetManagement';
import { SettingsProvider } from '../contexts/SettingsContext';

export const AssetPage: React.FC = () => {
  return (
    <SettingsProvider>
      <AssetManagement />
    </SettingsProvider>
  );
};
