import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, Home, Users, TrendingUp, TrendingDown, Tag, PieChart, UserPlus, UserCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ThemeSelector from './ThemeSelector';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-primary-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <span className="text-2xl font-bold">iTrack+</span>
            </Link>
            
            <div className="hidden md:flex space-x-4">
              <Link
                to="/dashboard"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <Home size={18} />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/income"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <TrendingUp size={18} />
                <span>Income</span>
              </Link>
              <Link
                to="/expenses"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <TrendingDown size={18} />
                <span>Expenses</span>
              </Link>
              <Link
                to="/categories"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <Tag size={18} />
                <span>Categories</span>
              </Link>
              <Link
                to="/budgets"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <PieChart size={18} />
                <span>Budgets</span>
              </Link>
              <Link
                to="/entity"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <Users size={18} />
                <span>Entity</span>
              </Link>
              <Link
                to="/members"
                className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                <UserPlus size={18} />
                <span>Members</span>
              </Link>
              {user?.is_superadmin && (
                <Link
                  to="/admin"
                  className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
                >
                  <Users size={18} />
                  <span>Admin</span>
                </Link>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="mr-4 hidden sm:block">
              <ThemeSelector />
            </div>
            <Link
              to="/profile"
              className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors text-sm"
            >
              <UserCircle size={18} />
              <span>{user?.username}</span>
            </Link>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 px-3 py-2 rounded-md hover:bg-primary-700 transition-colors"
            >
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
