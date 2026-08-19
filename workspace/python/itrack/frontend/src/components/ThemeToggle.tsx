import React, { useState, useRef, useEffect } from 'react';
import { Palette } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface ThemeOption {
  id: string;
  label: string;
  color: string;
  bg: string;
  textColor: string;
}

const DARK_THEMES: ThemeOption[] = [
  { id: 'dark',     label: 'Dark',     color: '#6366f1', bg: '#0d1117', textColor: '#e6edf3' },
  { id: 'midnight', label: 'Midnight', color: '#7c3aed', bg: '#06061a', textColor: '#d4d0f5' },
  { id: 'forest',   label: 'Forest',   color: '#22c55e', bg: '#0a1f0a', textColor: '#d1fae5' },
  { id: 'navy',     label: 'Navy',     color: '#64ffda', bg: '#020c1b', textColor: '#ccd6f6' },
  { id: 'rose',     label: 'Rose',     color: '#fb7185', bg: '#150508', textColor: '#fce7f3' },
  { id: 'amber',    label: 'Amber',    color: '#f59e0b', bg: '#120c00', textColor: '#fef3c7' },
];

const LIGHT_THEMES: ThemeOption[] = [
  { id: 'light',    label: 'Light',    color: '#2563eb', bg: '#f6f8fa', textColor: '#1a2332' },
  { id: 'warm',     label: 'Warm',     color: '#ea580c', bg: '#fef9f0', textColor: '#431407' },
  { id: 'mint',     label: 'Mint',     color: '#10b981', bg: '#f0fdf4', textColor: '#064e3b' },
  { id: 'lavender', label: 'Lavender', color: '#7c3aed', bg: '#faf5ff', textColor: '#2e1065' },
  { id: 'ocean',    label: 'Ocean',    color: '#0891b2', bg: '#ecfeff', textColor: '#083344' },
  { id: 'blossom',  label: 'Blossom',  color: '#e11d48', bg: '#fff1f2', textColor: '#4c0519' },
];

const ALL_THEMES = [...DARK_THEMES, ...LIGHT_THEMES];

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [panelPos, setPanelPos] = useState({ top: 0, left: 0 });

  const current = ALL_THEMES.find(t => t.id === theme) ?? DARK_THEMES[0];

  useEffect(() => {
    if (!open) return;
    const onMouseDown = (e: MouseEvent) => {
      if (
        !panelRef.current?.contains(e.target as Node) &&
        !triggerRef.current?.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    return () => document.removeEventListener('mousedown', onMouseDown);
  }, [open]);

  const handleToggle = () => {
    if (!open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const panelW = 292;
      const panelH = 360;
      const left = Math.min(rect.right + 12, window.innerWidth - panelW - 8);
      const top = Math.min(rect.top, window.innerHeight - panelH - 8);
      setPanelPos({ top: Math.max(8, top), left: Math.max(8, left) });
    }
    setOpen(prev => !prev);
  };

  const handleSelect = (id: string) => {
    setTheme(id as any);
    setOpen(false);
  };

  return (
    <>
      <button
        ref={triggerRef}
        onClick={handleToggle}
        title="Change theme"
        className="nav-item"
        style={{ color: open ? 'var(--text)' : undefined, background: open ? 'var(--surface-2)' : undefined }}
      >
        <div style={{
          width: 16, height: 16, borderRadius: '50%',
          background: current.color,
          flexShrink: 0,
          boxShadow: `0 0 6px ${current.color}99`,
        }} />
        <span>Theme</span>
        <Palette size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
      </button>

      {open && (
        <div
          ref={panelRef}
          style={{
            position: 'fixed',
            top: panelPos.top,
            left: panelPos.left,
            zIndex: 1000,
            width: 292,
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border)',
            borderRadius: 14,
            padding: '1rem',
            boxShadow: 'var(--shadow)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            animation: 'slideIn 0.2s cubic-bezier(0.16,1,0.3,1) forwards',
          }}
        >
          <ThemeGroup label="Dark" themes={DARK_THEMES} active={theme} onSelect={handleSelect} />
          <div style={{ height: 1, background: 'var(--border-subtle)', margin: '0.75rem 0' }} />
          <ThemeGroup label="Light" themes={LIGHT_THEMES} active={theme} onSelect={handleSelect} />
        </div>
      )}
    </>
  );
};

interface ThemeGroupProps {
  label: string;
  themes: ThemeOption[];
  active: string;
  onSelect: (id: string) => void;
}

const ThemeGroup: React.FC<ThemeGroupProps> = ({ label, themes, active, onSelect }) => (
  <div>
    <span style={{
      display: 'block',
      fontSize: '0.6875rem', fontWeight: 600,
      letterSpacing: '0.08em', textTransform: 'uppercase',
      color: 'var(--text-muted)',
      marginBottom: '0.5rem',
    }}>
      {label}
    </span>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
      {themes.map(t => (
        <ThemeCard key={t.id} theme={t} active={active === t.id} onSelect={onSelect} />
      ))}
    </div>
  </div>
);

interface ThemeCardProps {
  theme: ThemeOption;
  active: boolean;
  onSelect: (id: string) => void;
}

const ThemeCard: React.FC<ThemeCardProps> = ({ theme, active, onSelect }) => (
  <button
    onClick={() => onSelect(theme.id)}
    title={theme.label}
    style={{
      background: theme.bg,
      border: `2px solid ${active ? theme.color : 'transparent'}`,
      borderRadius: 8,
      padding: '0.5rem 0.5rem 0.375rem',
      cursor: 'pointer',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.375rem',
      alignItems: 'flex-start',
      transition: 'transform 0.15s, box-shadow 0.15s',
      boxShadow: active ? `0 0 0 3px ${theme.color}30` : 'none',
      outline: 'none',
    }}
    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.transform = 'translateY(-1px)'; }}
    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.transform = ''; }}
  >
    <div style={{ display: 'flex', gap: 4 }}>
      <div style={{ width: 9, height: 9, borderRadius: '50%', background: theme.color }} />
      <div style={{ width: 9, height: 9, borderRadius: '50%', background: `${theme.color}70` }} />
      <div style={{ width: 9, height: 9, borderRadius: '50%', background: `${theme.color}30` }} />
    </div>
    <span style={{
      fontSize: '0.6875rem', fontWeight: 600,
      color: active ? theme.color : theme.textColor,
      opacity: active ? 1 : 0.75,
      lineHeight: 1,
    }}>
      {theme.label}
    </span>
  </button>
);

export default ThemeToggle;
