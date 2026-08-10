import React, { useState, useEffect } from 'react';
import { TrendingUp, Plus, Edit2, Trash2, Filter } from 'lucide-react';
import { Transaction, TransactionInput } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import TransactionBulkInput from './TransactionBulkInput';

export const IncomeManagement: React.FC = () => {
  const [incomes, setIncomes] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showBulk, setShowBulk] = useState(false);
  const [editingIncome, setEditingIncome] = useState<Transaction | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('');

  const [formData, setFormData] = useState<TransactionInput>({
    description: '',
    amount: 0,
    type: 'income',
    category: '',
    date: new Date().toISOString().split('T')[0],
    mode: 'private',
    is_recurring: false,
    recurrence: undefined,
    recurrence_start: undefined,
  });

  const incomeCategories = ['Salary', 'Freelance', 'Investment', 'Business', 'Other'];

  useEffect(() => {
    loadIncomes();
  }, [filterCategory]);

  const loadIncomes = async () => {
    try {
      setLoading(true);
      const data = await transactionService.getTransactions({
        type: 'income',
        category: filterCategory || undefined,
      });
      setIncomes(data);
    } catch (err: any) {
      setError('Failed to load incomes');
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
        type: 'income' as const,
        date: new Date(formData.date).toISOString(),
        is_recurring: formData.is_recurring,
        recurrence: formData.is_recurring ? 'monthly' : undefined,
        recurrence_start: formData.is_recurring && formData.recurrence_start ? new Date(formData.recurrence_start).toISOString() : undefined,
      };

      if (editingIncome) {
        await transactionService.updateTransaction(editingIncome.id, dataToSubmit);
        setSuccess('Income updated successfully');
      } else {
        await transactionService.createTransaction(dataToSubmit);
        setSuccess('Income added successfully');
      }

      resetForm();
      loadIncomes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (income: Transaction) => {
    setEditingIncome(income);
    setFormData({
      description: income.description,
      amount: income.amount,
      type: 'income',
      category: income.category,
      date: new Date(income.date).toISOString().split('T')[0],
      mode: income.mode || 'private',
      is_recurring: (income as any).is_recurring || false,
      recurrence: (income as any).recurrence,
      recurrence_start: (income as any).recurrence_start ? new Date((income as any).recurrence_start).toISOString().split('T')[0] : undefined,
    });
    setShowForm(true);
  };

  const handleDelete = async (incomeId: string) => {
    if (!window.confirm('Are you sure you want to delete this income?')) {
      return;
    }

    try {
      await transactionService.deleteTransaction(incomeId);
      setSuccess('Income deleted successfully');
      loadIncomes();
    } catch (err: any) {
      setError('Failed to delete income');
    }
  };

  const resetForm = () => {
    setFormData({
      description: '',
      amount: 0,
      type: 'income',
      category: '',
      date: new Date().toISOString().split('T')[0],
      mode: 'private',
    });
    setEditingIncome(null);
    setShowForm(false);
  };

  const totalIncome = incomes.reduce((sum, income) => sum + income.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <TrendingUp className="text-green-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Income Management</h1>
            <p className="text-gray-600">Track and manage your income sources</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowForm(!showForm)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>{showForm ? 'Cancel' : 'Add Income'}</span>
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
      <div className="card bg-gradient-to-r from-green-500 to-emerald-600 text-white">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-green-100 text-sm">Total Income</p>
            <h2 className="text-4xl font-bold">${totalIncome.toFixed(2)}</h2>
            <p className="text-green-100 text-sm mt-1">{incomes.length} transactions</p>
          </div>
          <TrendingUp size={64} className="text-green-200 opacity-50" />
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {editingIncome ? 'Edit Income' : 'Add New Income'}
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
                  placeholder="e.g., Monthly Salary"
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
                  {incomeCategories.map((cat) => (
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

            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary flex-1">
                {editingIncome ? 'Update Income' : 'Add Income'}
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
          <TransactionBulkInput defaultType="income" onDone={() => { setShowBulk(false); loadIncomes(); }} />
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
            {incomeCategories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Income List */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Income History</h2>
        {loading ? (
          <p className="text-gray-600">Loading incomes...</p>
        ) : incomes.length === 0 ? (
          <p className="text-gray-600">No income transactions found. Add your first income!</p>
        ) : (
          <div className="space-y-3">
            {incomes.map((income) => (
              <div
                key={income.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <TrendingUp size={20} className="text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{income.description}</h3>
                      <p className="text-sm text-gray-600">
                        {income.category} • {new Date(income.date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-xl font-bold text-green-600">
                    +${income.amount.toFixed(2)}
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(income)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                      title="Edit"
                    >
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(income.id)}
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
