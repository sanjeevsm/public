import React from 'react';
import { TrendingUp, TrendingDown, Wallet, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { TransactionSummary } from '../types/transaction';
import { useSettings } from '../contexts/SettingsContext';

interface Props { summary: TransactionSummary; }

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
  gradientClass: string;
  positive?: boolean | null;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, sub, icon, gradientClass, positive }) => (
  <div className={`stat-card ${gradientClass}`} style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)', letterSpacing: '0.01em' }}>
        {label}
      </span>
      <div style={{
        width: 36, height: 36,
        background: 'var(--primary-soft)',
        borderRadius: 9,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--primary)',
      }}>
        {icon}
      </div>
    </div>

    <div>
      <div className="stat-value">{value}</div>
      {sub && (
        <div style={{ marginTop: '0.375rem', display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
          {positive === true  && <ArrowUpRight size={14} style={{ color: 'var(--success)' }} />}
          {positive === false && <ArrowDownRight size={14} style={{ color: 'var(--error)' }} />}
          <span>{sub}</span>
        </div>
      )}
    </div>
  </div>
);

export const DashboardSummary: React.FC<Props> = ({ summary }) => {
  const { formatCurrency } = useSettings();
  const fmt = formatCurrency;
  const balance = summary.total_balance;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
      <StatCard
        label="Net Balance"
        value={fmt(balance)}
        sub={balance >= 0 ? 'Surplus' : 'Deficit'}
        positive={balance >= 0 ? true : false}
        icon={<Wallet size={18} strokeWidth={1.75} />}
        gradientClass="gradient-balance"
      />
      <StatCard
        label="Total Income"
        value={fmt(summary.total_income)}
        sub={`${summary.income_count} transaction${summary.income_count !== 1 ? 's' : ''}`}
        positive={true}
        icon={<TrendingUp size={18} strokeWidth={1.75} style={{ color: 'var(--success)' }} />}
        gradientClass="gradient-income"
      />
      <StatCard
        label="Total Expenses"
        value={fmt(summary.total_expense)}
        sub={`${summary.expense_count} transaction${summary.expense_count !== 1 ? 's' : ''}`}
        positive={false}
        icon={<TrendingDown size={18} strokeWidth={1.75} style={{ color: 'var(--error)' }} />}
        gradientClass="gradient-expense"
      />
    </div>
  );
};
