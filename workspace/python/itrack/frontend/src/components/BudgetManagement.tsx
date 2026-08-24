import React, { useState, useEffect } from 'react';
import { PieChart, Plus, Edit2, Trash2, AlertTriangle, CheckCircle } from 'lucide-react';
import { Budget, BudgetCreate, BudgetProgress, BudgetPeriod, BudgetType } from '../types/budget';
import { budgetService } from '../services/budgetService';
import { useSettings } from '../contexts/SettingsContext';

export const BudgetManagement: React.FC = () => {
  const { formatCurrency, selectedCurrencies, currency: primaryCurrency } = useSettings();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [progress, setProgress] = useState<BudgetProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState<BudgetCreate>({
    name: '',
    amount: 0,
    period: 'monthly',
    budget_type: 'total',
    category: '',
    currency: primaryCurrency,
    start_date: new Date().toISOString().split('T')[0],
    alert_threshold: 80,
  });

  const categories = [
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
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [budgetsData, progressData] = await Promise.all([
        budgetService.getBudgets(true),
        budgetService.getBudgetsProgress(),
      ]);
      setBudgets(budgetsData);
      setProgress(progressData);
    } catch (err: any) {
      setError('Failed to load budgets');
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
        start_date: new Date(formData.start_date).toISOString(),
      };

      if (editingBudget) {
        await budgetService.updateBudget(editingBudget.id, dataToSubmit);
        setSuccess('Budget updated successfully');
      } else {
        await budgetService.createBudget(dataToSubmit);
        setSuccess('Budget created successfully');
      }

      resetForm();
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (budget: Budget) => {
    setEditingBudget(budget);
    setFormData({
      name: budget.name,
      amount: budget.amount,
      period: budget.period,
      budget_type: budget.budget_type,
      category: budget.category || '',
      currency: budget.currency,
      start_date: new Date(budget.start_date).toISOString().split('T')[0],
      alert_threshold: budget.alert_threshold,
    });
    setShowForm(true);
  };

  const handleDelete = async (budgetId: string) => {
    if (!window.confirm('Are you sure you want to delete this budget?')) {
      return;
    }

    try {
      await budgetService.deleteBudget(budgetId);
      setSuccess('Budget deleted successfully');
      loadData();
    } catch (err: any) {
      setError('Failed to delete budget');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      amount: 0,
      period: 'monthly',
      budget_type: 'total',
      category: '',
      currency: primaryCurrency,
      start_date: new Date().toISOString().split('T')[0],
      alert_threshold: 80,
    });
    setEditingBudget(null);
    setShowForm(false);
  };

  const getProgressBarColor = (progress: BudgetProgress) => {
    if (progress.is_exceeded) return 'bg-red-600';
    if (progress.is_alert) return 'bg-yellow-500';
    return 'bg-green-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <PieChart className="text-blue-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Budget Management</h1>
            <p className="text-gray-600">Set and track your spending limits</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>{showForm ? 'Cancel' : 'Create Budget'}</span>
        </button>
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

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {editingBudget ? 'Edit Budget' : 'Create New Budget'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  placeholder="e.g., Monthly Expenses"
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
                  Currency *
                </label>
                <select
                  required
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="input"
                >
                  {selectedCurrencies.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Only expenses in this currency count toward the budget
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Period *
                </label>
                <select
                  required
                  value={formData.period}
                  onChange={(e) => setFormData({ ...formData, period: e.target.value as BudgetPeriod })}
                  className="input"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Type *
                </label>
                <select
                  required
                  value={formData.budget_type}
                  onChange={(e) => setFormData({ ...formData, budget_type: e.target.value as BudgetType })}
                  className="input"
                >
                  <option value="total">Total Expenses</option>
                  <option value="category">Specific Category</option>
                </select>
              </div>

              {formData.budget_type === 'category' && (
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
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date *
                </label>
                <input
                  type="date"
                  required
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alert Threshold (%) *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  max="100"
                  value={formData.alert_threshold}
                  onChange={(e) => setFormData({ ...formData, alert_threshold: parseFloat(e.target.value) })}
                  className="input"
                  placeholder="80"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Alert when this percentage of budget is spent
                </p>
              </div>
            </div>

            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary flex-1">
                {editingBudget ? 'Update Budget' : 'Create Budget'}
              </button>
              <button type="button" onClick={resetForm} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Budget Progress Cards */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Active Budgets</h2>
        {loading ? (
          <p className="text-gray-600">Loading budgets...</p>
        ) : progress.length === 0 ? (
          <p className="text-gray-600">No active budgets. Create your first budget!</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {progress.map((p) => {
              const progressBarColor = getProgressBarColor(p);
              const progressWidth = Math.min(p.percentage_spent, 100);

              return (
                <div
                  key={p.budget_id}
                  className={`p-4 border-2 rounded-lg ${
                    p.is_exceeded
                      ? 'border-red-300 bg-red-50'
                      : p.is_alert
                      ? 'border-yellow-300 bg-yellow-50'
                      : 'border-green-300 bg-green-50'
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-800">{p.budget_name}</h3>
                      <p className="text-sm text-gray-600">
                        {p.category ? `${p.category} • ` : ''}
                        {p.period.charAt(0).toUpperCase() + p.period.slice(1)}
                        {` • ${p.currency}`}
                      </p>
                    </div>
                    {p.is_exceeded ? (
                      <AlertTriangle className="text-red-600" size={20} />
                    ) : p.is_alert ? (
                      <AlertTriangle className="text-yellow-600" size={20} />
                    ) : (
                      <CheckCircle className="text-green-600" size={20} />
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Spent</span>
                      <span className="font-semibold">{formatCurrency(p.spent_amount, p.currency)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Budget</span>
                      <span className="font-semibold">{formatCurrency(p.budget_amount, p.currency)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Remaining</span>
                      <span className={`font-semibold ${p.remaining_amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(p.remaining_amount, p.currency)}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-3">
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>{p.percentage_spent.toFixed(1)}% used</span>
                        {p.days_remaining !== undefined && p.days_remaining > 0 && (
                          <span>{p.days_remaining} days left</span>
                        )}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`${progressBarColor} h-3 rounded-full transition-all duration-500`}
                          style={{ width: `${progressWidth}%` }}
                        />
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-2 mt-3 pt-3 border-t">
                      <button
                        onClick={() => {
                          const budget = budgets.find(b => b.id === p.budget_id);
                          if (budget) handleEdit(budget);
                        }}
                        className="flex-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition flex items-center justify-center space-x-1"
                      >
                        <Edit2 size={14} />
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handleDelete(p.budget_id)}
                        className="flex-1 px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition flex items-center justify-center space-x-1"
                      >
                        <Trash2 size={14} />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
