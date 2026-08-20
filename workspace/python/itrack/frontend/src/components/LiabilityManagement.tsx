import React, { useState, useEffect } from 'react';
import { TrendingDown, Plus, Edit2, Trash2, Filter, Lock, Users } from 'lucide-react';
import { Transaction, TransactionInput, TransactionMode } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

export const LiabilityManagement: React.FC = () => {
  const { formatCurrency, selectedCurrencies, currency: primaryCurrency } = useSettings();
  const { user } = useAuth();
  const hasEntity = !!user?.entity_id;
  const [liabilities, setLiabilities] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingLiability, setEditingLiability] = useState<Transaction | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('');

  // Sort currencies: primary first, then alphabetically
  const sortedCurrencies = React.useMemo(() => {
    const sorted = [...selectedCurrencies];
    sorted.sort((a, b) => {
      if (a === primaryCurrency) return -1;
      if (b === primaryCurrency) return 1;
      return a.localeCompare(b);
    });
    return sorted;
  }, [selectedCurrencies, primaryCurrency]);

  const [activeCurrency, setActiveCurrency] = useState(sortedCurrencies[0] || primaryCurrency || 'USD');

  // Update active currency when sorted currencies change
  useEffect(() => {
    if (sortedCurrencies.length > 0 && !sortedCurrencies.includes(activeCurrency)) {
      setActiveCurrency(sortedCurrencies[0]);
    }
  }, [sortedCurrencies, activeCurrency]);

  const [formData, setFormData] = useState<TransactionInput>({
    description: '',
    amount: 0,
    type: 'liability',
    category: '',
    date: new Date().toISOString().split('T')[0],
    mode: 'private',
    currency: activeCurrency,
  });

  const liabilityCategories = ['Mortgages', 'Loans', 'Credit Cards', 'Other'];

  useEffect(() => {
    loadLiabilities();
  }, [filterCategory, activeCurrency]);

  const loadLiabilities = async () => {
    try {
      setLoading(true);
      const data = await transactionService.getTransactions({
        type: 'liability',
        category: filterCategory || undefined,
      });
      setLiabilities(data.filter(l => l.currency === activeCurrency));
    } catch (err: any) {
      setError('Failed to load liabilities');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const dataToSubmit = {
        ...formData,
        type: 'liability' as const,
        date: new Date(formData.date).toISOString(),
        currency: activeCurrency,
      };

      if (editingLiability) {
        await transactionService.updateTransaction(editingLiability.id, dataToSubmit);
        setSuccess('Liability updated successfully');
      } else {
        await transactionService.createTransaction(dataToSubmit);
        setSuccess('Liability added successfully');
      }

      resetForm();
      loadLiabilities();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (liability: Transaction) => {
    setEditingLiability(liability);
    setFormData({
      description: liability.description,
      amount: liability.amount,
      type: 'liability',
      category: liability.category,
      date: new Date(liability.date).toISOString().split('T')[0],
      mode: liability.mode || 'private',
      currency: liability.currency,
    });
    setShowForm(true);
  };

  const handleDelete = async (liabilityId: string) => {
    if (!window.confirm('Are you sure you want to delete this liability?')) {
      return;
    }

    try {
      await transactionService.deleteTransaction(liabilityId);
      setSuccess('Liability deleted successfully');
      loadLiabilities();
    } catch (err: any) {
      setError('Failed to delete liability');
    }
  };

  const resetForm = () => {
    setFormData({
      description: '',
      amount: 0,
      type: 'liability',
      category: '',
      date: new Date().toISOString().split('T')[0],
      mode: 'private',
      currency: activeCurrency,
    });
    setEditingLiability(null);
    setShowForm(false);
  };

  const totalLiabilities = liabilities.reduce((sum, liability) => sum + liability.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header with Currency Tabs */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <TrendingDown className="text-orange-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Liability Management</h1>
            <p className="text-gray-600">Track and manage your liabilities</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>{showForm ? 'Cancel' : 'Add Liability'}</span>
        </button>
      </div>

      {/* Currency Tabs */}
      {selectedCurrencies.length > 1 && (
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {sortedCurrencies.map(curr => (
              <button
                key={curr}
                onClick={() => setActiveCurrency(curr)}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: 8,
                  border: `2px solid ${activeCurrency === curr ? 'var(--primary)' : 'var(--border)'}`,
                  background: activeCurrency === curr ? 'var(--primary-soft)' : 'var(--surface)',
                  color: activeCurrency === curr ? 'var(--primary)' : 'var(--text-secondary)',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {curr}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-700">
          {success}
        </div>
      )}

      {/* Summary Card */}
      <div className="card bg-gradient-to-r from-orange-500 to-red-600 text-white">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-orange-100 text-sm">Total Liabilities ({activeCurrency})</p>
            <h2 className="text-4xl font-bold">{formatCurrency(totalLiabilities, activeCurrency)}</h2>
            <p className="text-orange-100 text-sm mt-1">{liabilities.length} liabilities</p>
          </div>
          <TrendingDown size={64} className="text-orange-200 opacity-50" />
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {editingLiability ? 'Edit Liability' : 'Add New Liability'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description *
                </label>
                <input
                  type="text"
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="input"
                  placeholder="e.g., Home Mortgage"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount *
                </label>
                <input
                  type="number"
                  required
                  min="0.01"
                  step="0.01"
                  value={formData.amount || ''}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
                  className="input"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  required
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="input"
                >
                  <option value="">Select category</option>
                  {liabilityCategories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date *
                </label>
                <input
                  type="date"
                  required
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="input"
                />
              </div>
            </div>

            {/* Visibility */}
            {hasEntity && (
              <div>
                <label className="label">Entity Visibility</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {(['private', 'shared'] as TransactionMode[]).map(m => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setFormData({ ...formData, mode: m })}
                      style={{
                        flex: 1, padding: '0.5rem 0.75rem', borderRadius: 8,
                        border: `1px solid ${formData.mode === m ? 'var(--primary)' : 'var(--border)'}`,
                        background: formData.mode === m ? 'var(--primary-soft)' : 'var(--surface)',
                        color: formData.mode === m ? 'var(--primary)' : 'var(--text-secondary)',
                        fontWeight: 500, fontSize: '0.875rem', cursor: 'pointer',
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      {m === 'private' ? <Lock size={14} /> : <Users size={14} />}
                      {m === 'private' ? 'Private' : 'Shared with Entity'}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary flex-1">
                {editingLiability ? 'Update Liability' : 'Add Liability'}
              </button>
              <button type="button" onClick={resetForm} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter */}
      <div className="card">
        <div className="flex items-center space-x-3">
          <Filter size={20} className="text-gray-600" />
          <label className="text-sm font-medium text-gray-700">Filter by Category:</label>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="input max-w-xs"
          >
            <option value="">All Categories</option>
            {liabilityCategories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Liability List */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Liability List</h2>
        {loading ? (
          <p className="text-gray-600">Loading liabilities...</p>
        ) : liabilities.length === 0 ? (
          <p className="text-gray-600">No liabilities found. Add your first liability!</p>
        ) : (
          <div className="space-y-3">
            {liabilities.map((liability) => (
              <div
                key={liability.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                      <TrendingDown size={20} className="text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{liability.description}</h3>
                      <p className="text-sm text-gray-600" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
                        {liability.category} • {new Date(liability.date).toLocaleDateString()}
                        {hasEntity && liability.mode && (
                          <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.2rem',
                            fontSize: '0.6875rem', fontWeight: 600,
                            padding: '0.1rem 0.45rem', borderRadius: 99,
                            background: liability.mode === 'shared' ? 'var(--primary-soft)' : 'var(--surface-2)',
                            color: liability.mode === 'shared' ? 'var(--primary)' : 'var(--text-muted)',
                            border: `1px solid ${liability.mode === 'shared' ? 'var(--primary)' : 'var(--border)'}`,
                          }}>
                            {liability.mode === 'shared' ? <Users size={9} /> : <Lock size={9} />}
                            {liability.mode}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-xl font-bold text-orange-600">
                    {formatCurrency(liability.amount, liability.currency)}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(liability)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                      title="Edit"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(liability.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      title="Delete"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
