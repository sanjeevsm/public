import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Navbar } from '../components/Navbar';
import { EntityCreateForm } from '../components/EntityCreateForm';
import { EntityDashboardSummary } from '../components/EntityDashboardSummary';
import { EntityManagement } from '../components/EntityManagement';
import { Entity, EntitySummary } from '../types/entity';
import { entityService } from '../services/entityService';

export const EntityPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [entity, setEntity] = useState<Entity | null>(null);
  const [summary, setSummary] = useState<EntitySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [includePrivate, setIncludePrivate] = useState(false);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'management'>('dashboard');

  const isAdmin = user?.entity_role === 'admin';

  useEffect(() => {
    loadEntityData();
  }, []);

  useEffect(() => {
    if (entity) {
      loadSummary();
    }
  }, [entity, includePrivate]);

  const loadEntityData = async () => {
    setLoading(true);
    setError('');

    try {
      const entityData = await entityService.getMyEntity();
      setEntity(entityData);
    } catch (err: any) {
      if (err.response?.status === 404) {
        // User doesn't have an entity
        setEntity(null);
      } else {
        setError(err.response?.data?.detail || 'Failed to load entity');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!entity) return;

    try {
      const summaryData = await entityService.getEntitySummary(entity.id, includePrivate);
      setSummary(summaryData);
    } catch (err: any) {
      console.error('Failed to load summary:', err);
    }
  };

  const handleEntityCreated = async () => {
    setShowCreateForm(false);
    await loadEntityData();
    await refreshUser();
  };

  const handleEntityUpdated = async () => {
    await loadEntityData();
    await refreshUser();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No entity - show create form
  if (!entity) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            {error && (
              <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
                {error}
              </div>
            )}

            {!showCreateForm && (
              <div className="bg-white rounded-lg shadow-lg p-8 text-center">
                <div className="text-6xl mb-4">🏠</div>
                <h1 className="text-3xl font-bold text-gray-800 mb-4">
                  Create Your Entity
                </h1>
                <p className="text-gray-600 mb-6">
                  You're not part of any entity yet. Create a household, office, or custom group
                  to start collaborating with others while maintaining your privacy.
                </p>
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition text-lg font-semibold"
                >
                  Create Entity
                </button>

                <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl mb-2">👨‍👩‍👧‍👦</div>
                    <h3 className="font-semibold text-gray-800 mb-1">Family</h3>
                    <p className="text-sm text-gray-600">
                      Track household expenses and income together
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl mb-2">💼</div>
                    <h3 className="font-semibold text-gray-800 mb-1">Office</h3>
                    <p className="text-sm text-gray-600">
                      Manage team expenses and budgets
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl mb-2">🎨</div>
                    <h3 className="font-semibold text-gray-800 mb-1">Custom</h3>
                    <p className="text-sm text-gray-600">
                      Create your own type for any group
                    </p>
                  </div>
                </div>
              </div>
            )}

            {showCreateForm && (
              <EntityCreateForm
                onSuccess={handleEntityCreated}
                onCancel={() => setShowCreateForm(false)}
              />
            )}
          </div>
        </div>
      </div>
    );
  }

  // Has entity - show dashboard
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Dashboard
            </button>
            <button
              onClick={() => setActiveTab('management')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'management'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              ⚙️ Management
            </button>
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div>
            {/* Admin Toggle */}
            {isAdmin && (
              <div className="mb-6 bg-white rounded-lg shadow p-4 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">Admin View</h3>
                  <p className="text-sm text-gray-600">
                    Toggle to see all transactions including private ones
                  </p>
                </div>
                <label className="flex items-center cursor-pointer">
                  <span className="mr-3 text-sm font-medium text-gray-700">
                    {includePrivate ? 'All Transactions' : 'Shared Only'}
                  </span>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={includePrivate}
                      onChange={(e) => setIncludePrivate(e.target.checked)}
                      className="sr-only"
                    />
                    <div
                      className={`block w-14 h-8 rounded-full ${
                        includePrivate ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    ></div>
                    <div
                      className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition ${
                        includePrivate ? 'transform translate-x-6' : ''
                      }`}
                    ></div>
                  </div>
                </label>
              </div>
            )}

            {/* Summary */}
            {summary && (
              <EntityDashboardSummary
                summary={summary}
                isAdmin={isAdmin}
                includePrivate={includePrivate}
              />
            )}
          </div>
        )}

        {/* Management Tab */}
        {activeTab === 'management' && user && (
          <EntityManagement
            entity={entity}
            currentUserId={user.id}
            isAdmin={isAdmin}
            onUpdate={handleEntityUpdated}
          />
        )}
      </div>
    </div>
  );
};
