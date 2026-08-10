import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const themes = [
  { id: 'dark', label: 'Dark', bg: '#0b1220' },
  { id: 'light', label: 'Light', bg: '#ffffff' },
  { id: 'midnight', label: 'Midnight', bg: '#020617' },
  { id: 'forest', label: 'Forest', bg: '#0b2b0b' },
  { id: 'navy', label: 'Navy', bg: '#001529' },
  { id: 'warm', label: 'Warm', bg: '#fff7ed' },
];

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-2">
      {themes.map((t) => (
        <button
          key={t.id}
          onClick={() => setTheme(t.id as any)}
          title={t.label}
          className={`w-7 h-7 rounded-full border-2 ${theme === t.id ? 'ring-2 ring-offset-1' : ''}`}
          style={{ backgroundColor: t.bg }}
        />
      ))}
    </div>
  );
};

export default ThemeToggle;
