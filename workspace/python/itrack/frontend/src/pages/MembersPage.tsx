import React from 'react';
import { Navbar } from '../components/Navbar';
import { MemberManagement } from '../components/MemberManagement';

export const MembersPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <MemberManagement />
      </main>
    </div>
  );
};
