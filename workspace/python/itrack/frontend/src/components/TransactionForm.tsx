import React, { useState } from 'react';
import { PlusCircle } from 'lucide-react';
import { TransactionInput, TransactionType, TransactionMode } from '../types/transaction';
import { transactionService } from '../services/transactionService';

interface Props {
  onSuccess: () => void;
  hasEntity?: boolean;
}

export const TransactionForm: React.FC<Props> = ({ onSuccess, hasEntity = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<TransactionInput>({
    description: '',
    amount: 0,
    type: 'expense',
    category: '',
    date: new Date().toISOString().split('T')[0],
    mode: 'private', // Default to private for safety
  });

  const categories = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Bills & Utilities',
    'Healthcare',
    'Education',
    'Salary',
    'Freelance',
    'Investment',
    'Other',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await transactionService.createTransaction({
        ...formData,
        date: new Date(formData.date).toISOString(),
      });
      
      // Reset form
      setFormData({
        description: '',
        amount: 0,
        type: 'expense',
        category: '',
        date: new Date().toISOString().split('T')[0],
        mode: 'private',
      });
      
      setIsOpen(false);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create transaction');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-primary flex items-center space-x-2"
      >
        <PlusCircle size={20} />
        <span>Add Transaction</span>
      </button>
    );
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Add New Transaction</h2>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="income"
                checked={formData.type === 'income'}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as TransactionType })}
                className="mr-2"
              />
              Income
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="expense"
                checked={formData.type === 'expense'}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as TransactionType })}
                className="mr-2"
              />
              Expense
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <input
            type="text"
            required
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="input"
            placeholder="Enter description"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount
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
            Category
          </label>
          <select
            required
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="input"
          >
            <option value="">Select a category</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date
          </label>
          <input
            type="date"
            required
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            className="input"
          />
        </div>

        {/* Transaction Mode (only show if user has entity) */}
        {hasEntity && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Visibility
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="private"
                  checked={formData.mode === 'private'}
                  onChange={(e) => setFormData({ ...formData, mode: e.target.value as TransactionMode })}
                  className="mr-2"
                />
                <span className="flex items-center">
                  🔒 Private
                  <span className="ml-2 text-xs text-gray-500">(Only you and admins)</span>
                </span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="shared"
                  checked={formData.mode === 'shared'}
                  onChange={(e) => setFormData({ ...formData, mode: e.target.value as TransactionMode })}
                  className="mr-2"
                />
                <span className="flex items-center">
                  👥 Shared
                  <span className="ml-2 text-xs text-gray-500">(Visible to all members)</span>
                </span>
              </label>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              💡 Private transactions are visible only to you and entity admins. Shared transactions are visible to all entity members.
            </p>
          </div>
        )}

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Adding...' : 'Add Transaction'}
          </button>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
