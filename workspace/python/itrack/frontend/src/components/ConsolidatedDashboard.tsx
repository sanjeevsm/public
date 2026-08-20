import React, { useState, useEffect } from 'react';
import { Wallet, TrendingUp, TrendingDown, PieChart, DollarSign } from 'lucide-react';
import { useSettings } from '../contexts/SettingsContext';
import { transactionService } from '../services/transactionService';
import { TransactionSummary } from '../types/transaction';

export const ConsolidatedDashboard: React.FC = () => {
  const { formatCurrency, selectedCurrencies } = useSettings();
  const [summaries, setSummaries] = useState<TransactionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSummaries();
  }, [selectedCurrencies]);

  const loadSummaries = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await transactionService.getMultiCurrencySummary(selectedCurrencies);
      setSummaries(data);
    } catch (err: any) {
      setError('Failed to load summaries');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p className="text-gray-600">Loading consolidated dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        
        {/* Header */}
        <div className="page-header" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <Wallet size={28} style={{ color: 'var(--primary)' }} />
          <div>
            <h1 className="page-title">Consolidated Net Worth</h1>
            <p className="page-subtitle">Your financial overview across all currencies</p>
          </div>
        </div>

        {/* Currency Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {summaries.map(summary => (
            <div key={summary.currency} className="card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                    {summary.currency}
                  </h3>
                  <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text)' }}>
                    {formatCurrency(summary.net_worth, summary.currency)}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Net Worth</p>
                </div>
                <DollarSign size={40} style={{ color: 'var(--primary)', opacity: 0.2 }} />
              </div>

              {/* Detailed Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.25rem' }}>
                    <TrendingUp size={14} style={{ color: '#10B981' }} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Income</span>
                  </div>
                  <p style={{ fontSize: '1.125rem', fontWeight: 700, color: '#10B981' }}>
                    {formatCurrency(summary.total_income, summary.currency)}
                  </p>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.income_count} transactions</p>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.25rem' }}>
                    <TrendingDown size={14} style={{ color: '#EF4444' }} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Expenses</span>
                  </div>
                  <p style={{ fontSize: '1.125rem', fontWeight: 700, color: '#EF4444' }}>
                    {formatCurrency(summary.total_expense, summary.currency)}
                  </p>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.expense_count} transactions</p>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.25rem' }}>
                    <PieChart size={14} style={{ color: '#3B82F6' }} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Assets</span>
                  </div>
                  <p style={{ fontSize: '1.125rem', fontWeight: 700, color: '#3B82F6' }}>
                    {formatCurrency(summary.total_assets, summary.currency)}
                  </p>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.asset_count} items</p>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.25rem' }}>
                    <PieChart size={14} style={{ color: '#F97316' }} />
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Liabilities</span>
                  </div>
                  <p style={{ fontSize: '1.125rem', fontWeight: 700, color: '#F97316' }}>
                    {formatCurrency(summary.total_liabilities, summary.currency)}
                  </p>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{summary.liability_count} items</p>
                </div>
              </div>

              {/* Balance Calculation */}
              <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--surface-2)', borderRadius: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Income - Expenses</span>
                  <span style={{ fontWeight: 600, color: summary.total_balance >= 0 ? '#10B981' : '#EF4444' }}>
                    {formatCurrency(summary.total_balance, summary.currency)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Assets - Liabilities</span>
                  <span style={{ fontWeight: 600, color: (summary.total_assets - summary.total_liabilities) >= 0 ? '#3B82F6' : '#F97316' }}>
                    {formatCurrency(summary.total_assets - summary.total_liabilities, summary.currency)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', paddingTop: '0.5rem', borderTop: '1px dashed var(--border)', marginTop: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)' }}>Net Worth</span>
                  <span style={{ fontWeight: 700, color: summary.net_worth >= 0 ? 'var(--primary)' : '#EF4444' }}>
                    {formatCurrency(summary.net_worth, summary.currency)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Important Note */}
        <div className="card" style={{ padding: '1rem', background: 'var(--primary-soft)', borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
            <DollarSign size={20} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '0.125rem' }} />
            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text)', marginBottom: '0.25rem' }}>
                Multi-Currency Tracking
              </h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Each currency is tracked separately. Net worth is calculated independently for each currency. 
                No automatic conversion is applied between currencies.
              </p>
            </div>
          </div>
        </div>

        {/* Overall Summary Table */}
        {summaries.length > 0 && (
          <div className="card" style={{ marginTop: '2rem', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text)' }}>
              Summary Table
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Currency</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Income</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Expenses</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Assets</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Liabilities</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem', fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Net Worth</th>
                  </tr>
                </thead>
                <tbody>
                  {summaries.map(summary => (
                    <tr key={summary.currency} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--text)' }}>{summary.currency}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', color: '#10B981', fontWeight: 600 }}>
                        {formatCurrency(summary.total_income, summary.currency)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', color: '#EF4444', fontWeight: 600 }}>
                        {formatCurrency(summary.total_expense, summary.currency)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', color: '#3B82F6', fontWeight: 600 }}>
                        {formatCurrency(summary.total_assets, summary.currency)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', color: '#F97316', fontWeight: 600 }}>
                        {formatCurrency(summary.total_liabilities, summary.currency)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', color: summary.net_worth >= 0 ? 'var(--primary)' : '#EF4444', fontWeight: 700, fontSize: '1rem' }}>
                        {formatCurrency(summary.net_worth, summary.currency)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
