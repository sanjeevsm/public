import React from 'react';
import { TrendingUp, TrendingDown, Wallet, Users, Lock, Unlock } from 'lucide-react';
import { EntitySummary } from '../types/entity';
import { useSettings } from '../contexts/SettingsContext';

interface Props {
  summary: EntitySummary;
  isAdmin: boolean;
  includePrivate: boolean;
  isMonthly?: boolean;
}

export const EntityDashboardSummary: React.FC<Props> = ({ summary, isAdmin, includePrivate, isMonthly = false }) => {
  const { formatCurrency } = useSettings();
  const fmt = formatCurrency;

  const balance = summary.total_balance;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* Entity header */}
      <div style={{
        background: 'linear-gradient(135deg, var(--primary), #7c3aed)',
        borderRadius: 14,
        padding: '1.5rem',
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', opacity: 0.75 }}>
            Entity Dashboard
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0.25rem 0 0.5rem' }}>{summary.entity_name}</h2>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span style={{ background: 'rgba(255,255,255,0.18)', borderRadius: 20, padding: '0.2rem 0.75rem', fontSize: '0.75rem', fontWeight: 500 }}>
              {isAdmin ? '👑 Admin' : '👤 Member'}
            </span>
            {isAdmin && (
              <span style={{ background: 'rgba(255,255,255,0.18)', borderRadius: 20, padding: '0.2rem 0.75rem', fontSize: '0.75rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                {includePrivate ? <Unlock size={11} /> : <Lock size={11} />}
                {includePrivate ? 'All Transactions' : 'Shared Only'}
              </span>
            )}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', opacity: 0.75 }}>{isMonthly ? 'Monthly Surplus' : 'Net Balance'}</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
            {fmt(balance)}
          </div>
        </div>
      </div>

      {/* Summary stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="stat-card gradient-balance">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{isMonthly ? 'Monthly Surplus' : 'Net Balance'}</span>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: 'var(--primary-soft)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <Wallet size={16} />
            </div>
          </div>
          <div className="stat-value" style={{ color: balance >= 0 ? 'var(--success)' : 'var(--error)' }}>{fmt(balance)}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>{summary.transaction_count} transactions</div>
        </div>

        <div className="stat-card gradient-income">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{isMonthly ? 'Monthly Income' : 'Total Income'}</span>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: 'rgba(34,197,94,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <TrendingUp size={16} style={{ color: 'var(--success)' }} />
            </div>
          </div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{fmt(summary.total_income)}</div>
        </div>

        <div className="stat-card gradient-expense">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{isMonthly ? 'Monthly Expenses' : 'Total Expenses'}</span>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: 'rgba(239,68,68,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <TrendingDown size={16} style={{ color: 'var(--error)' }} />
            </div>
          </div>
          <div className="stat-value" style={{ color: 'var(--error)' }}>{fmt(summary.total_expense)}</div>
        </div>
      </div>

      {/* Shared vs All comparison (admin with private) */}
      {isAdmin && includePrivate && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 className="section-title">Shared vs All Transactions</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {[
              { label: 'Shared Only', income: summary.shared_income, expense: summary.shared_expense, balance: summary.shared_balance, count: summary.shared_transaction_count },
              { label: 'All (Shared + Private)', income: summary.total_income, expense: summary.total_expense, balance: summary.total_balance, count: summary.transaction_count },
            ].map(col => (
              <div key={col.label}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{col.label}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {[
                    { k: 'Balance', v: fmt(col.balance), c: col.balance >= 0 ? 'var(--success)' : 'var(--error)' },
                    { k: 'Income',  v: fmt(col.income),  c: 'var(--success)' },
                    { k: 'Expense', v: fmt(col.expense), c: 'var(--error)' },
                    { k: 'Count',   v: String(col.count), c: 'var(--text)' },
                  ].map(r => (
                    <div key={r.k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>{r.k}</span>
                      <span style={{ fontSize: '0.875rem', fontWeight: 600, color: r.c }}>{r.v}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Per-member breakdown (admin with private) */}
      {isAdmin && includePrivate && Object.keys(summary.member_breakdown).length > 0 && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={15} />
            Per-Member Breakdown
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {['Member', 'Income', 'Expenses', 'Balance'].map(h => (
                    <th key={h} style={{ textAlign: h === 'Member' ? 'left' : 'right', padding: '0.5rem 0.75rem', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(summary.member_breakdown).map(([uid, mb]) => (
                  <tr key={uid} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '0.75rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text)' }}>{mb.username}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600, color: 'var(--success)' }}>{fmt(mb.income)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600, color: 'var(--error)' }}>{fmt(mb.expense)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 700, color: mb.balance >= 0 ? 'var(--success)' : 'var(--error)' }}>{fmt(mb.balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};
