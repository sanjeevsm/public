import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, TrendingDown, Tag, PieChart,
  Building2, Users, UserCircle, LogOut, ShieldCheck, Menu, X,
  Wallet, Settings, DollarSign,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from './ThemeToggle';

const navItems = [
  { to: '/dashboard',     icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/consolidated',  icon: DollarSign,      label: 'Net Worth' },
  { to: '/income',        icon: TrendingUp,      label: 'Income' },
  { to: '/expenses',      icon: TrendingDown,    label: 'Expenses' },
  { to: '/assets',        icon: Wallet,          label: 'Assets' },
  { to: '/liabilities',   icon: PieChart,        label: 'Liabilities' },
  { to: '/categories',    icon: Tag,             label: 'Categories' },
  { to: '/budgets',       icon: PieChart,        label: 'Budgets' },
];

const entityItems = [
  { to: '/entity',  icon: Building2, label: 'Entity' },
  { to: '/members', icon: Users,     label: 'Members' },
];

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const sidebar = (
    <aside
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'var(--nav-bg)',
        borderRight: '1px solid var(--border)',
        padding: '0',
        overflowY: 'auto',
      }}
    >
      {/* Brand */}
      <div style={{ padding: '1.5rem 1.25rem 1rem', borderBottom: '1px solid var(--border-subtle)' }}>
        <NavLink to="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: 32, height: 32,
            background: 'var(--primary)',
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px var(--primary-glow)',
          }}>
            <Wallet size={18} color="#fff" strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--text)', letterSpacing: '-0.02em' }}>
            iTrack<span style={{ color: 'var(--primary)' }}>+</span>
          </span>
        </NavLink>
      </div>

      {/* Main nav */}
      <nav style={{ flex: 1, padding: '1rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        <span style={{ fontSize: '0.6875rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0 0.5rem', marginBottom: '0.25rem' }}>
          Overview
        </span>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={17} strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}

        <span style={{ fontSize: '0.6875rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0 0.5rem', marginTop: '1.25rem', marginBottom: '0.25rem' }}>
          Entity
        </span>
        {entityItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={17} strokeWidth={1.75} />
            <span>{label}</span>
          </NavLink>
        ))}

        {user?.is_superadmin && (
          <>
            <span style={{ fontSize: '0.6875rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)', padding: '0 0.5rem', marginTop: '1.25rem', marginBottom: '0.25rem' }}>
              Admin
            </span>
            <NavLink
              to="/admin"
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <ShieldCheck size={17} strokeWidth={1.75} />
              <span>Admin Panel</span>
            </NavLink>
          </>
        )}
      </nav>

      {/* Bottom section */}
      <div style={{ padding: '0.75rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {/* Theme toggle */}
        <ThemeToggle />

        {/* Settings */}
        <NavLink
          to="/settings"
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <Settings size={17} strokeWidth={1.75} />
          <span>Settings</span>
        </NavLink>

        {/* Profile */}
        <NavLink
          to="/profile"
          onClick={() => setMobileOpen(false)}
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <UserCircle size={17} strokeWidth={1.75} />
          <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.username}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.email}
            </span>
          </div>
        </NavLink>

        {/* Logout */}
        <button className="nav-item" onClick={handleLogout} style={{ color: 'var(--error)' }}>
          <LogOut size={17} strokeWidth={1.75} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div
        className="sidebar-desktop"
        style={{
          position: 'fixed', top: 0, left: 0, bottom: 0,
          width: 232,
          zIndex: 40,
          display: 'none',
        }}
      >
        {sidebar}
      </div>

      {/* Mobile topbar */}
      <header
        className="sidebar-mobile-bar"
        style={{
          display: 'none',
          position: 'fixed', top: 0, left: 0, right: 0,
          height: 56,
          background: 'var(--nav-bg)',
          borderBottom: '1px solid var(--border)',
          zIndex: 40,
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1rem',
        }}
      >
        <NavLink to="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: 28, height: 28, background: 'var(--primary)', borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Wallet size={15} color="#fff" />
          </div>
          <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)' }}>
            iTrack<span style={{ color: 'var(--primary)' }}>+</span>
          </span>
        </NavLink>
        <button className="btn btn-ghost btn-icon" onClick={() => setMobileOpen(true)}>
          <Menu size={20} />
        </button>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex' }}>
          <div
            style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
            onClick={() => setMobileOpen(false)}
          />
          <div style={{ position: 'relative', width: 260, height: '100%', zIndex: 1 }}>
            <button
              className="btn btn-ghost btn-icon"
              style={{ position: 'absolute', top: '1rem', right: '1rem', zIndex: 2 }}
              onClick={() => setMobileOpen(false)}
            >
              <X size={18} />
            </button>
            {sidebar}
          </div>
        </div>
      )}

      {/* Responsive styles */}
      <style>{`
        @media (min-width: 768px) {
          .sidebar-desktop { display: block !important; }
          .sidebar-mobile-bar { display: none !important; }
        }
        @media (max-width: 767px) {
          .sidebar-desktop { display: none !important; }
          .sidebar-mobile-bar { display: flex !important; }
        }
      `}</style>
    </>
  );
};
