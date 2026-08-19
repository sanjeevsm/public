import React from 'react';
import { MemberManagement } from '../components/MemberManagement';

export const MembersPage: React.FC = () => (
  <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
    <main className="container mx-auto px-4 py-8">
      <MemberManagement />
    </main>
  </div>
);
