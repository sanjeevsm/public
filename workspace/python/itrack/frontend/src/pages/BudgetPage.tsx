import React from 'react';
import { BudgetManagement } from '../components/BudgetManagement';

export const BudgetPage: React.FC = () => (
  <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
    <main className="container mx-auto px-4 py-8">
      <BudgetManagement />
    </main>
  </div>
);
