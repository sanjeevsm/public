import React from 'react';
import { IncomeManagement } from '../components/IncomeManagement';

export const IncomePage: React.FC = () => (
  <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
    <main className="container mx-auto px-4 py-8">
      <IncomeManagement />
    </main>
  </div>
);
