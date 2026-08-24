import React from 'react';
import { TrendingUp, TrendingDown, Wallet, Users, Lock, Unlock } from 'lucide-react';
import { EntitySummary } from '../types/entity';
import { useSettings } from '../contexts/SettingsContext';

interface Props {
  summary: EntitySummary;
  isAdmin: boolean;
  includePrivate: boolean;
  isMonthly?: boolean;
  compact?: boolean;
  currency?: string;
}

export const EntityDashboardSummary: React.FC<Props> = ({ summary, isAdmin, includePrivate, isMonthly = false, compact = false, currency }) => {
  const { formatCurrency } = useSettings();
  const fmt = (v: number) => formatCurrency(v, currency);

  const balance = summary.total_balance;
  const netAssets = (summary.total_assets || 0) - (summary.total_liabilities || 0);
  const netWorth = summary.net_worth ?? (balance + netAssets);

  if (compact) {
    return (
      <div>
        <div style={{
          background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
          borderRadius: 10, padding: '1rem', color: '#fff',
          textAlign: 'center', marginBottom: '0.75rem',
          boxShadow: '0 4px 12px rgba(59,130,246,0.3)',
        }}>
          <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>{isMonthly ? 'Monthly Surplus' : 'Net Worth'}</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{fmt(isMonthly ? balance : netWorth)}</div>
          {!isMonthly && (
            <div style={{ fontSize: '0.7rem', opacity: 0.85, marginTop: '0.2rem' }}>
              Balance {fmt(balance)} · Net Assets {fmt(netAssets)}
            </div>
          )}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
          {[
            { label: isMonthly ? 'Surplus' : 'Cash Balance', value: fmt(balance),              color: balance >= 0 ? 'var(--success)' : 'var(--error)' },
            { label: isMonthly ? 'Income'  : 'Total Income',  value: fmt(summary.total_income), color: 'var(--success)' },
            { label: isMonthly ? 'Expenses': 'Total Expenses',value: fmt(summary.total_expense),color: 'var(--error)' },
            { label: 'Assets',      value: fmt(summary.total_assets || 0),       color: '#3B82F6' },
            { label: 'Liabilities', value: fmt(summary.total_liabilities || 0),  color: '#F97316' },
            { label: 'Net Assets',  value: fmt(netAssets), color: netAssets >= 0 ? '#3B82F6' : '#F97316' },
          ].map(t => (
            <div key={t.label} style={{ padding: '0.625rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>{t.label}</div>
              <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: t.color }}>{t.value}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

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
          <div style={{ fontSize: '0.75rem', opacity: 0.75 }}>{isMonthly ? 'Monthly Surplus' : 'Net Worth'}</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em' }}>
            {fmt(isMonthly ? balance : netWorth)}
          </div>
          {!isMonthly && (
            <div style={{ fontSize: '0.7rem', opacity: 0.85, marginTop: '0.25rem' }}>
              Balance {fmt(balance)} + Net Assets {fmt(netAssets)}
            </div>
          )}
        </div>
      </div>

      {/* Summary stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="stat-card gradient-balance">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{isMonthly ? 'Monthly Surplus' : 'Cash Balance'}</span>
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

      {/* Assets & Liabilities breakdown (all-time view only) */}
      {!isMonthly && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 className="section-title">Financial Breakdown</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Assets</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#3B82F6' }}>{fmt(summary.total_assets || 0)}</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Liabilities</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F97316' }}>{fmt(summary.total_liabilities || 0)}</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Net Assets</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: netAssets >= 0 ? '#3B82F6' : '#F97316' }}>{fmt(netAssets)}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Assets − Liabilities</div>
            </div>
            <div style={{ padding: '0.75rem', background: 'var(--surface)', borderRadius: 8 }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Net Worth</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: netWorth >= 0 ? '#10B981' : '#EF4444' }}>{fmt(netWorth)}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Balance + Net Assets</div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', padding: '0.875rem', background: 'linear-gradient(135deg, var(--primary-soft) 0%, transparent 100%)', borderRadius: 8, border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <strong>Net Worth</strong> = (Income − Expenses) + (Assets − Liabilities)<br />
              = ({fmt(summary.total_income)} − {fmt(summary.total_expense)}) + ({fmt(summary.total_assets || 0)} − {fmt(summary.total_liabilities || 0)})<br />
              = <strong style={{ color: 'var(--primary)' }}>{fmt(netWorth)}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Shared vs All comparison (admin with private) */}
      {isAdmin && includePrivate && (
        <div className="card" style={{ padding: '1.25rem' }}>
          <h3 className="section-title">Shared vs All Transactions</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {[
              {
                label: 'Shared Only',
                income: summary.shared_income, expense: summary.shared_expense, balance: summary.shared_balance,
                assets: summary.shared_assets, liabilities: summary.shared_liabilities,
                netAssets: (summary.shared_assets || 0) - (summary.shared_liabilities || 0),
                count: summary.shared_transaction_count,
              },
              {
                label: 'All (Shared + Private)',
                income: summary.total_income, expense: summary.total_expense, balance: summary.total_balance,
                assets: summary.total_assets, liabilities: summary.total_liabilities,
                netAssets: (summary.total_assets || 0) - (summary.total_liabilities || 0),
                count: summary.transaction_count,
              },
            ].map(col => (
              <div key={col.label}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>{col.label}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {[
                    { k: 'Cash Balance', v: fmt(col.balance),    c: col.balance >= 0 ? 'var(--success)' : 'var(--error)' },
                    { k: 'Income',       v: fmt(col.income),     c: 'var(--success)' },
                    { k: 'Expense',      v: fmt(col.expense),    c: 'var(--error)' },
                    { k: 'Assets',       v: fmt(col.assets),     c: '#3B82F6' },
                    { k: 'Liabilities',  v: fmt(col.liabilities),c: '#F97316' },
                    { k: 'Net Assets',   v: fmt(col.netAssets),  c: col.netAssets >= 0 ? '#3B82F6' : '#F97316' },
                    { k: 'Net Worth',    v: fmt(col.balance + col.netAssets), c: (col.balance + col.netAssets) >= 0 ? '#10B981' : '#EF4444' },
                    { k: 'Count',        v: String(col.count),   c: 'var(--text)' },
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
                  {['Member', 'Income', 'Expenses', 'Cash Balance', 'Assets', 'Liabilities', 'Net Assets', 'Net Worth'].map(h => (
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
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600, color: '#3B82F6' }}>{fmt(mb.assets || 0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600, color: '#F97316' }}>{fmt(mb.liabilities || 0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 600, color: (mb.net_assets || 0) >= 0 ? '#3B82F6' : '#F97316' }}>{fmt(mb.net_assets || 0)}</td>
                    <td style={{ padding: '0.75rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: 700, color: (mb.net_worth || 0) >= 0 ? '#10B981' : '#EF4444' }}>{fmt(mb.net_worth || 0)}</td>
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
