import React from 'react';
import { TrendingUp, TrendingDown, Wallet } from 'lucide-react';
import { TransactionSummary } from '../types/transaction';

interface Props {
  summary: TransactionSummary;
}

export const DashboardSummary: React.FC<Props> = ({ summary }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* Total Balance */}
      <div className="card bg-gradient-to-br from-primary-500 to-primary-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Total Balance</p>
            <p className="text-3xl font-bold mt-2">
              {formatCurrency(summary.total_balance)}
            </p>
          </div>
          <Wallet size={48} className="opacity-80" />
        </div>
      </div>

      {/* Total Income */}
      <div className="card bg-gradient-to-br from-green-500 to-green-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Total Income</p>
            <p className="text-3xl font-bold mt-2">
              {formatCurrency(summary.total_income)}
            </p>
            <p className="text-sm mt-2 opacity-90">
              {summary.income_count} transactions
            </p>
          </div>
          <TrendingUp size={48} className="opacity-80" />
        </div>
      </div>

      {/* Total Expenses */}
      <div className="card bg-gradient-to-br from-red-500 to-red-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90">Total Expenses</p>
            <p className="text-3xl font-bold mt-2">
              {formatCurrency(summary.total_expense)}
            </p>
            <p className="text-sm mt-2 opacity-90">
              {summary.expense_count} transactions
            </p>
          </div>
          <TrendingDown size={48} className="opacity-80" />
        </div>
      </div>
    </div>
  );
};
