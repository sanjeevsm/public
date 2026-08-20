import React, { useState, useEffect } from 'react';
import { TrendingDown, Plus, Edit2, Trash2, Filter, Lock, Users } from 'lucide-react';
import { Transaction, TransactionInput, TransactionMode } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import TransactionBulkInput from './TransactionBulkInput';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

export const ExpenseManagement: React.FC = () => {
  const { formatCurrency } = useSettings();
  const { user } = useAuth();
  const hasEntity = !!user?.entity_id;
  const [expenses, setExpenses] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showBulk, setShowBulk] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Transaction | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('');

  const [formData, setFormData] = useState<TransactionInput>({
    description: '',
    amount: 0,
    type: 'expense',
    category: '',
    date: new Date().toISOString().split('T')[0],
    mode: 'private',
    is_recurring: false,
    recurrence: undefined,
    recurrence_start: undefined,
  });

  const expenseCategories = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Bills & Utilities',
    'Healthcare',
    'Education',
    'Housing',
    'Other',
  ];

  useEffect(() => {
    loadExpenses();
  }, [filterCategory]);

  const loadExpenses = async () => {
    try {
      setLoading(true);
      const data = await transactionService.getTransactions({
        type: 'expense',
        category: filterCategory || undefined,
      });
      setExpenses(data);
    } catch (err: any) {
      setError('Failed to load expenses');
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
        type: 'expense' as const,
        date: new Date(formData.date).toISOString(),
        is_recurring: formData.is_recurring,
        recurrence: formData.is_recurring ? 'monthly' : undefined,
        recurrence_start: formData.is_recurring && formData.recurrence_start ? new Date(formData.recurrence_start).toISOString() : undefined,
      };

      if (editingExpense) {
        await transactionService.updateTransaction(editingExpense.id, dataToSubmit);
        setSuccess('Expense updated successfully');
      } else {
        await transactionService.createTransaction(dataToSubmit);
        setSuccess('Expense added successfully');
      }

      resetForm();
      loadExpenses();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (expense: Transaction) => {
    setEditingExpense(expense);
    setFormData({
      description: expense.description,
      amount: expense.amount,
      type: 'expense',
      category: expense.category,
      date: new Date(expense.date).toISOString().split('T')[0],
      mode: expense.mode || 'private',
      is_recurring: (expense as any).is_recurring || false,
      recurrence: (expense as any).recurrence,
      recurrence_start: (expense as any).recurrence_start ? new Date((expense as any).recurrence_start).toISOString().split('T')[0] : undefined,
    });
    setShowForm(true);
  };

  const handleDelete = async (expenseId: string) => {
    if (!window.confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    try {
      await transactionService.deleteTransaction(expenseId);
      setSuccess('Expense deleted successfully');
      loadExpenses();
    } catch (err: any) {
      setError('Failed to delete expense');
    }
  };

  const resetForm = () => {
    setFormData({
      description: '',
      amount: 0,
      type: 'expense',
      category: '',
      date: new Date().toISOString().split('T')[0],
      mode: 'private',
    });
    setEditingExpense(null);
    setShowForm(false);
  };

  const totalExpense = expenses.reduce((sum, expense) => sum + expense.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <TrendingDown className="text-red-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Expense Management</h1>
            <p className="text-gray-600">Track and manage your expenses</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>{showForm ? 'Cancel' : 'Add Expense'}</span>
          </button>
          <button
            onClick={() => setShowBulk(!showBulk)}
            className="btn btn-outline flex items-center"
          >
            Bulk Input
          </button>
        </div>
      </div>

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
      <div className="card bg-gradient-to-r from-red-500 to-pink-600 text-white">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-red-100 text-sm">Total Expenses</p>
            <h2 className="text-4xl font-bold">{formatCurrency(totalExpense, false)}</h2>
            <p className="text-red-100 text-sm mt-1">{expenses.length} transactions</p>
          </div>
          <TrendingDown size={64} className="text-red-200 opacity-50" />
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {editingExpense ? 'Edit Expense' : 'Add New Expense'}
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
                  placeholder="e.g., Grocery Shopping"
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
                  {expenseCategories.map((cat) => (
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

              <div>
                <label className="flex items-center cursor-pointer space-x-2">
                  <input
                    type="checkbox"
                    checked={!!formData.is_recurring}
                    onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="font-medium">Monthly recurring</span>
                </label>
                {formData.is_recurring && (
                  <div className="mt-2">
                    <label className="block text-sm text-gray-700 mb-1">Recurrence start</label>
                    <input
                      type="date"
                      value={formData.recurrence_start || new Date().toISOString().split('T')[0]}
                      onChange={(e) => setFormData({ ...formData, recurrence_start: e.target.value })}
                      className="input"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Visibility — only shown when user belongs to an entity */}
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
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>
                  {formData.mode === 'shared'
                    ? 'This transaction will be visible to all entity members.'
                    : 'This transaction is only visible to you.'}
                </p>
              </div>
            )}

            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary flex-1">
                {editingExpense ? 'Update Expense' : 'Add Expense'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {showBulk && (
        <div>
          <TransactionBulkInput defaultType="expense" onDone={() => { setShowBulk(false); loadExpenses(); }} />
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
            {expenseCategories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Expense List */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Expense History</h2>
        {loading ? (
          <p className="text-gray-600">Loading expenses...</p>
        ) : expenses.length === 0 ? (
          <p className="text-gray-600">No expense transactions found. Add your first expense!</p>
        ) : (
          <div className="space-y-3">
            {expenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                      <TrendingDown size={20} className="text-red-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{expense.description}</h3>
                      <p className="text-sm text-gray-600" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
                        {expense.category} • {new Date(expense.date).toLocaleDateString()}
                        {hasEntity && expense.mode && (
                          <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.2rem',
                            fontSize: '0.6875rem', fontWeight: 600,
                            padding: '0.1rem 0.45rem', borderRadius: 99,
                            background: expense.mode === 'shared' ? 'var(--primary-soft)' : 'var(--surface-2)',
                            color: expense.mode === 'shared' ? 'var(--primary)' : 'var(--text-muted)',
                            border: `1px solid ${expense.mode === 'shared' ? 'var(--primary)' : 'var(--border)'}`,
                          }}>
                            {expense.mode === 'shared' ? <Users size={9} /> : <Lock size={9} />}
                            {expense.mode}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-xl font-bold text-red-600">
                    -{formatCurrency(expense.amount, false)}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(expense)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                      title="Edit"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(expense.id)}
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
