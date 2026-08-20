import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { EntityPage } from './pages/EntityPage';
import { IncomePage } from './pages/IncomePage';
import { ExpensePage } from './pages/ExpensePage';
import { CategoryPage } from './pages/CategoryPage';
import { BudgetPage } from './pages/BudgetPage';
import { MembersPage } from './pages/MembersPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminPage } from './pages/AdminPage';
import { SettingsPage } from './pages/SettingsPage';
import { AssetPage } from './pages/AssetPage';
import { LiabilityPage } from './pages/LiabilityPage';
import { ConsolidatedPage } from './pages/ConsolidatedPage';
import './index.css';

const Protected: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute>
    <Layout>{children}</Layout>
  </ProtectedRoute>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login"    element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard"  element={<Protected><DashboardPage /></Protected>} />
          <Route path="/consolidated" element={<Protected><ConsolidatedPage /></Protected>} />
          <Route path="/entity"     element={<Protected><EntityPage /></Protected>} />
          <Route path="/income"     element={<Protected><IncomePage /></Protected>} />
          <Route path="/expenses"   element={<Protected><ExpensePage /></Protected>} />
          <Route path="/assets"     element={<Protected><AssetPage /></Protected>} />
          <Route path="/liabilities" element={<Protected><LiabilityPage /></Protected>} />
          <Route path="/categories" element={<Protected><CategoryPage /></Protected>} />
          <Route path="/budgets"    element={<Protected><BudgetPage /></Protected>} />
          <Route path="/members"    element={<Protected><MembersPage /></Protected>} />
          <Route path="/admin"      element={<Protected><AdminPage /></Protected>} />
          <Route path="/profile"    element={<Protected><ProfilePage /></Protected>} />
          <Route path="/settings"   element={<Protected><SettingsPage /></Protected>} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
