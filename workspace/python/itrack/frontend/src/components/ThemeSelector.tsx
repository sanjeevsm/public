import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

export const ThemeSelector: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const options = [
    'dark',
    'light',
    'midnight',
    'forest',
    'navy',
    'warm',
  ] as const;

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value as any)}
      className="bg-primary-600 text-white px-2 py-1 rounded"
    >
      {options.map(o => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  );
};

export default ThemeSelector;
