import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const themes = [
  { id: 'dark', label: 'Dark', color: '#6366f1' },
  { id: 'light', label: 'Light', color: '#2563eb' },
  { id: 'midnight', label: 'Midnight', color: '#7c3aed' },
  { id: 'forest', label: 'Forest', color: '#16a34a' },
  { id: 'navy', label: 'Navy', color: '#06b6d4' },
  { id: 'warm', label: 'Warm', color: '#f97316' },
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
          style={{ backgroundColor: t.color }}
        />
      ))}
    </div>
  );
};

export default ThemeToggle;
