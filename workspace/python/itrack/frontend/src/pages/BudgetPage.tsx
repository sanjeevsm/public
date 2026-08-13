import React from 'react';
import { Navbar } from '../components/Navbar';
import { BudgetManagement } from '../components/BudgetManagement';

export const BudgetPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <BudgetManagement />
      </main>
    </div>
  );
};
