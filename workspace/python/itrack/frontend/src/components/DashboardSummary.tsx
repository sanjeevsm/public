import React from 'react';
import { TrendingUp, TrendingDown, Wallet, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { TransactionSummary } from '../types/transaction';
import { useSettings } from '../contexts/SettingsContext';

interface Props { 
  summary: TransactionSummary; 
  compact?: boolean; 
}

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

export const DashboardSummary: React.FC<Props> = ({ summary, compact = false }) => {
  const { formatCurrency } = useSettings();
  const currency = summary.currency || 'USD';
  const balance = summary.total_balance; // Income - Expenses
  const netAssets = (summary.total_assets || 0) - (summary.total_liabilities || 0);
  const netWorth = balance + netAssets; // Complete Net Worth

  return (
    <>
      {/* Net Worth Highlight */}
      {compact ? (
        // Compact mode: Show simple Net Worth card
        <div style={{ 
          padding: '1rem', 
          marginBottom: '1rem', 
          background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', 
          borderRadius: 10, 
          color: 'white', 
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
        }}>
          <div style={{ fontSize: '0.75rem', opacity: 0.95, marginBottom: '0.25rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>Net Worth</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>{formatCurrency(netWorth, currency)}</div>
          <div style={{ fontSize: '0.7rem', opacity: 0.9, marginTop: '0.25rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>
            Balance {formatCurrency(balance, currency)} + Net Assets {formatCurrency(netAssets, currency)}
          </div>
        </div>
      ) : (
        // Full mode: Show detailed Net Worth banner with calculation
        (summary.total_assets !== undefined || summary.total_liabilities !== undefined) && (
        <div className="card" style={{ 
          padding: '1.25rem', 
          marginBottom: '1.25rem', 
          background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', 
          color: 'white',
          boxShadow: '0 4px 16px rgba(59, 130, 246, 0.3)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.8125rem', opacity: 0.95, marginBottom: '0.25rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>Current Net Worth ({currency})</div>
              <div style={{ fontSize: '2rem', fontWeight: 700, textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>{formatCurrency(netWorth, currency)}</div>
              <div style={{ fontSize: '0.75rem', opacity: 0.9, marginTop: '0.25rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>
                Balance {formatCurrency(balance, currency)} + Net Assets {formatCurrency(netAssets, currency)}
              </div>
            </div>
            <div style={{ textAlign: 'right', opacity: 0.95 }}>
              <div style={{ fontSize: '0.75rem', marginBottom: '0.5rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>Calculation:</div>
              <div style={{ fontSize: '0.8125rem', fontFamily: 'monospace', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>
                ({formatCurrency(summary.total_income, currency)} - {formatCurrency(summary.total_expense, currency)})
              </div>
              <div style={{ fontSize: '0.75rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>+</div>
              <div style={{ fontSize: '0.8125rem', fontFamily: 'monospace', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>
                ({formatCurrency(summary.total_assets || 0, currency)} - {formatCurrency(summary.total_liabilities || 0, currency)})
              </div>
              <div style={{ fontSize: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.4)', marginTop: '0.25rem', paddingTop: '0.25rem', textShadow: '0 1px 2px rgba(0,0,0,0.2)' }}>= {formatCurrency(netWorth, currency)}</div>
            </div>
          </div>
        </div>
        )
      )}

      {/* Main Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.25rem' }}>
        <StatCard
          label="Cash Balance"
          value={formatCurrency(balance, currency)}
          sub="Income - Expenses"
          positive={balance >= 0 ? true : false}
          icon={<Wallet size={18} strokeWidth={1.75} />}
          gradientClass="gradient-balance"
        />
        <StatCard
          label="Total Income"
          value={formatCurrency(summary.total_income, currency)}
          sub={`${summary.income_count} transaction${summary.income_count !== 1 ? 's' : ''}`}
          positive={true}
          icon={<TrendingUp size={18} strokeWidth={1.75} style={{ color: 'var(--success)' }} />}
          gradientClass="gradient-income"
        />
        <StatCard
          label="Total Expenses"
          value={formatCurrency(summary.total_expense, currency)}
          sub={`${summary.expense_count} transaction${summary.expense_count !== 1 ? 's' : ''}`}
          positive={false}
          icon={<TrendingDown size={18} strokeWidth={1.75} style={{ color: 'var(--error)' }} />}
          gradientClass="gradient-expense"
        />
      </div>

      {/* Assets & Liabilities Breakdown (only in non-compact mode) */}
      {!compact && (summary.total_assets !== undefined || summary.total_liabilities !== undefined) && (
        <div className="card" style={{ padding: '1.5rem', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text)', marginBottom: '1rem' }}>Financial Breakdown</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Assets</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#3B82F6' }}>
                {formatCurrency(summary.total_assets || 0, currency)}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.asset_count || 0} items</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Liabilities</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F97316' }}>
                {formatCurrency(summary.total_liabilities || 0, currency)}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.liability_count || 0} items</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Balance</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: balance >= 0 ? '#10B981' : '#EF4444' }}>
                {formatCurrency(balance, currency)}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Income - Expenses</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Net Assets</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: (summary.total_assets || 0) - (summary.total_liabilities || 0) >= 0 ? '#3B82F6' : '#F97316' }}>
                {formatCurrency((summary.total_assets || 0) - (summary.total_liabilities || 0), currency)}
              </div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Assets - Liabilities</div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', padding: '0.875rem', background: 'linear-gradient(135deg, var(--primary-soft) 0%, transparent 100%)', borderRadius: 8, border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text)', marginBottom: '0.5rem' }}>💡 Net Worth Calculation</div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <strong>Net Worth</strong> = Cash Balance + Net Assets<br />
              = (Income - Expenses) + (Assets - Liabilities)<br />
              = ({formatCurrency(summary.total_income, currency)} - {formatCurrency(summary.total_expense, currency)}) + ({formatCurrency(summary.total_assets || 0, currency)} - {formatCurrency(summary.total_liabilities || 0, currency)})<br />
              = <strong style={{ color: 'var(--primary)' }}>{formatCurrency(netWorth, currency)}</strong>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
