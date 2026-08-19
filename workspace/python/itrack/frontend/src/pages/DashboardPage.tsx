import React, { useEffect, useState } from 'react';
import { Activity, CalendarDays, RefreshCw } from 'lucide-react';
import { TransactionSummary } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import { DashboardSummary } from '../components/DashboardSummary';
import { TransactionList } from '../components/TransactionList';
import { TransactionForm } from '../components/TransactionForm';
import { ImportExport } from '../components/ImportExport';
import { CategoryChart } from '../components/CategoryChart';
import { EntityStatusBanner } from '../components/EntityStatusBanner';
import { ForecastView } from '../components/ForecastView';
import { useAuth } from '../contexts/AuthContext';

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

type ViewMode = 'all-time' | 'monthly' | 'forecast';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('all-time');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    if (viewMode !== 'forecast') fetchSummary();
  }, [refreshTrigger, viewMode, selectedYear, selectedMonth]);

  const fetchSummary = async () => {
    setIsLoading(true);
    try {
      const data = viewMode === 'monthly'
        ? await transactionService.getMonthlySummary(selectedYear, selectedMonth)
        : await transactionService.getSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => setRefreshTrigger(p => p + 1);

  if (isLoading && !summary && viewMode !== 'forecast') {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>

        {/* Page header */}
        <div className="page-header" style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">Financial Dashboard</h1>
            <p className="page-subtitle">
              {viewMode === 'forecast'
                ? 'Balance forecast by scenario'
                : viewMode === 'monthly'
                ? `${MONTHS[selectedMonth - 1]} ${selectedYear}`
                : 'All-time overview'}
            </p>
          </div>

          {/* Period controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            {/* View mode toggle */}
            <div style={{
              display: 'flex',
              background: 'var(--surface-2)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              padding: '3px',
            }}>
              {(['all-time', 'monthly', 'forecast'] as const).map(mode => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  style={{
                    padding: '0.375rem 0.875rem',
                    borderRadius: 7,
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    background: viewMode === mode ? 'var(--primary)' : 'transparent',
                    color: viewMode === mode ? '#fff' : 'var(--text-secondary)',
                    display: 'flex', alignItems: 'center', gap: '0.375rem',
                  }}
                >
                  {mode === 'forecast' && <Activity size={13} />}
                  {mode === 'all-time' ? 'All-time' : mode === 'monthly' ? 'Monthly' : 'Forecast'}
                </button>
              ))}
            </div>

            {/* Month/year selectors (only for monthly view) */}
            {viewMode === 'monthly' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CalendarDays size={15} style={{ color: 'var(--text-muted)' }} />
                <select
                  value={selectedMonth}
                  onChange={e => setSelectedMonth(+e.target.value)}
                  className="input"
                  style={{ width: 'auto', paddingTop: '0.375rem', paddingBottom: '0.375rem' }}
                >
                  {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
                <input
                  type="number"
                  value={selectedYear}
                  onChange={e => setSelectedYear(+e.target.value)}
                  className="input"
                  style={{ width: 90, paddingTop: '0.375rem', paddingBottom: '0.375rem' }}
                />
              </div>
            )}

            {viewMode !== 'forecast' && (
              <button className="btn btn-ghost btn-sm" onClick={handleRefresh} title="Refresh">
                <RefreshCw size={15} />
              </button>
            )}
          </div>
        </div>

        {/* Entity banner */}
        <EntityStatusBanner hasEntity={!!user?.entity_id} />

        {/* ── Forecast view ─────────────────────────────────────── */}
        {viewMode === 'forecast' && (
          <div className="animate-slide-up">
            <ForecastView />
          </div>
        )}

        {/* ── Normal views (all-time / monthly) ─────────────────── */}
        {viewMode !== 'forecast' && (
          <>
            {summary && (
              <div className="animate-slide-up">
                <DashboardSummary summary={summary} />
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
              {summary && (
                <div className="card animate-slide-up stagger-1">
                  <CategoryChart summary={summary} />
                </div>
              )}
              <div className="card animate-slide-up stagger-2">
                <h2 className="section-title">Quick Actions</h2>
                <ImportExport onImportSuccess={handleRefresh} />
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }} className="animate-slide-up stagger-3">
              <TransactionForm onSuccess={handleRefresh} hasEntity={!!user?.entity_id} />
            </div>

            <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
              <TransactionList
                refreshTrigger={refreshTrigger}
                onUpdate={handleRefresh}
                onDelete={handleRefresh}
                showEntityInfo={!!user?.entity_id}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};
