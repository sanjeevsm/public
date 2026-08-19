import React from 'react';
import { CategoryManagement } from '../components/CategoryManagement';

export const CategoryPage: React.FC = () => (
  <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
    <main className="container mx-auto px-4 py-8">
      <CategoryManagement />
    </main>
  </div>
);
