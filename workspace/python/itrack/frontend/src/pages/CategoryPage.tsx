import React from 'react';
import { Navbar } from '../components/Navbar';
import { CategoryManagement } from '../components/CategoryManagement';

export const CategoryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <CategoryManagement />
      </main>
    </div>
  );
};
