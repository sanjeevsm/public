import React from 'react';
import { ExpenseManagement } from '../components/ExpenseManagement';

export const ExpensePage: React.FC = () => (
  <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
    <main className="container mx-auto px-4 py-8">
      <ExpenseManagement />
    </main>
  </div>
);
