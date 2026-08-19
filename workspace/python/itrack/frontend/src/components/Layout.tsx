import React from 'react';
import { Navbar } from './Navbar';

interface Props {
  children: React.ReactNode;
}

export const Layout: React.FC<Props> = ({ children }) => {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg)' }}>
      <Navbar />
      {/* Content area offset for sidebar on desktop, top bar on mobile */}
      <main
        style={{ flex: 1, minWidth: 0 }}
        className="layout-main"
      >
        {children}
      </main>
      <style>{`
        @media (min-width: 768px) {
          .layout-main {
            margin-left: 232px;
          }
        }
        @media (max-width: 767px) {
          .layout-main {
            margin-left: 0;
            margin-top: 56px;
          }
        }
      `}</style>
    </div>
  );
};
