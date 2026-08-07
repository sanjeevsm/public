import React from 'react';
import { EntitySummary } from '../types/entity';

interface EntityDashboardSummaryProps {
  summary: EntitySummary;
  isAdmin: boolean;
  includePrivate: boolean;
}

export const EntityDashboardSummary: React.FC<EntityDashboardSummaryProps> = ({
  summary,
  isAdmin,
  includePrivate
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Entity Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-2">{summary.entity_name}</h2>
        <div className="flex items-center space-x-4 text-sm">
          <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
            {isAdmin ? '👑 Admin View' : '👤 Member View'}
          </span>
          {isAdmin && includePrivate && (
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
              🔓 All Transactions
            </span>
          )}
          {isAdmin && !includePrivate && (
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
              🔒 Shared Only
            </span>
          )}
        </div>
      </div>

      {/* Overall Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Balance</h3>
          <p className={`text-3xl font-bold ${
            summary.total_balance >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatCurrency(summary.total_balance)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Income</h3>
          <p className="text-3xl font-bold text-green-600">
            {formatCurrency(summary.total_income)}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Expenses</h3>
          <p className="text-3xl font-bold text-red-600">
            {formatCurrency(summary.total_expense)}
          </p>
        </div>
      </div>

      {/* Shared vs All Comparison (Admin only with private) */}
      {isAdmin && includePrivate && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Shared vs All Transactions
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="border-r border-gray-200 pr-4">
              <h4 className="text-sm font-medium text-gray-500 mb-3">Shared Only</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Balance:</span>
                  <span className="font-semibold">{formatCurrency(summary.shared_balance)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Income:</span>
                  <span className="font-semibold text-green-600">{formatCurrency(summary.shared_income)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Expense:</span>
                  <span className="font-semibold text-red-600">{formatCurrency(summary.shared_expense)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Count:</span>
                  <span className="font-semibold">{summary.shared_transaction_count}</span>
                </div>
              </div>
            </div>
            <div className="pl-4">
              <h4 className="text-sm font-medium text-gray-500 mb-3">All (Shared + Private)</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Balance:</span>
                  <span className="font-semibold">{formatCurrency(summary.total_balance)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Income:</span>
                  <span className="font-semibold text-green-600">{formatCurrency(summary.total_income)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Expense:</span>
                  <span className="font-semibold text-red-600">{formatCurrency(summary.total_expense)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Count:</span>
                  <span className="font-semibold">{summary.transaction_count}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Per-Member Breakdown (Admin only with private) */}
      {isAdmin && includePrivate && Object.keys(summary.member_breakdown).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Per-Member Breakdown
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Member</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Income</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Expenses</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Balance</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(summary.member_breakdown).map(([userId, breakdown]) => (
                  <tr key={userId} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm font-medium text-gray-800">
                      {breakdown.username}
                    </td>
                    <td className="py-3 px-4 text-sm text-right text-green-600 font-semibold">
                      {formatCurrency(breakdown.income)}
                    </td>
                    <td className="py-3 px-4 text-sm text-right text-red-600 font-semibold">
                      {formatCurrency(breakdown.expense)}
                    </td>
                    <td className={`py-3 px-4 text-sm text-right font-bold ${
                      breakdown.balance >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(breakdown.balance)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Transaction Count Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Transaction Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{summary.transaction_count}</p>
            <p className="text-sm text-gray-500 mt-1">Total Transactions</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{summary.shared_transaction_count}</p>
            <p className="text-sm text-gray-500 mt-1">Shared</p>
          </div>
          {isAdmin && includePrivate && (
            <>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  {summary.transaction_count - summary.shared_transaction_count}
                </p>
                <p className="text-sm text-gray-500 mt-1">Private</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {Object.keys(summary.member_breakdown).length}
                </p>
                <p className="text-sm text-gray-500 mt-1">Members</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
