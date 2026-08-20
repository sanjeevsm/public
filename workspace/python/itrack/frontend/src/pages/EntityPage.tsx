import React, { useState, useEffect } from 'react';
import { Activity, CalendarDays, RefreshCw, Settings2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';
import { EntityCreateForm } from '../components/EntityCreateForm';
import { EntityDashboardSummary } from '../components/EntityDashboardSummary';
import { EntityManagement } from '../components/EntityManagement';
import { CategoryChart } from '../components/CategoryChart';
import { ForecastView } from '../components/ForecastView';
import { Entity, EntitySummary } from '../types/entity';
import { entityService } from '../services/entityService';

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
type DashView = 'all-time' | 'monthly' | 'forecast';
type MainTab = 'dashboard' | 'management';

export const EntityPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const { selectedCurrencies, currency: primaryCurrency } = useSettings();
  const [entity, setEntity] = useState<Entity | null>(null);
  const [summary, setSummary] = useState<EntitySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [includePrivate, setIncludePrivate] = useState(true);
  const [mainTab, setMainTab] = useState<MainTab>('dashboard');
  const [dashView, setDashView] = useState<DashView>('all-time');
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);
  const [selectedCurrency, setSelectedCurrency] = useState(primaryCurrency);

  // Update selected currency when primary changes
  useEffect(() => {
    setSelectedCurrency(primaryCurrency);
  }, [primaryCurrency]);

  const isAdmin = user?.entity_role === 'admin';

  useEffect(() => { loadEntityData(); }, []);

  useEffect(() => {
    if (entity && dashView !== 'forecast') loadSummary();
  }, [entity, includePrivate, dashView, selectedYear, selectedMonth, refreshTick, selectedCurrency]);

  const loadEntityData = async () => {
    setLoading(true);
    setError('');
    try {
      const entityData = await entityService.getMyEntity();
      setEntity(entityData);
    } catch (err: any) {
      if (err.response?.status !== 404) setError(err.response?.data?.detail || 'Failed to load entity');
      else setEntity(null);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!entity) return;
    setSummaryLoading(true);
    try {
      const data = await entityService.getEntitySummary(
        entity.id,
        isAdmin ? includePrivate : false,
        dashView === 'monthly' ? selectedMonth : undefined,
        dashView === 'monthly' ? selectedYear : undefined,
        selectedCurrency,
      );
      setSummary(data);
    } catch (err: any) {
      console.error('Failed to load summary:', err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleEntityCreated = async () => {
    setShowCreateForm(false);
    await loadEntityData();
    await refreshUser();
  };

  const handleEntityUpdated = async () => {
    await loadEntityData();
    await refreshUser();
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  // No entity — show create form
  if (!entity) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
        <div style={{ maxWidth: 640, margin: '0 auto' }}>
          {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

          {!showCreateForm ? (
            <div className="card" style={{ padding: '2.5rem', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏠</div>
              <h1 className="page-title">Create Your Entity</h1>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9375rem' }}>
                You're not part of any entity yet. Create a household, office, or custom group to collaborate while maintaining privacy.
              </p>
              <button className="btn btn-primary" onClick={() => setShowCreateForm(true)}>
                Create Entity
              </button>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '2rem', textAlign: 'left' }}>
                {[
                  { emoji: '👨‍👩‍👧‍👦', title: 'Family',  desc: 'Track household expenses and income together' },
                  { emoji: '💼',       title: 'Office',  desc: 'Manage team expenses and budgets' },
                  { emoji: '🎨',       title: 'Custom',  desc: 'Create your own type for any group' },
                ].map(({ emoji, title, desc }) => (
                  <div key={title} style={{ background: 'var(--surface-2)', borderRadius: 10, padding: '1rem' }}>
                    <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{emoji}</div>
                    <div style={{ fontWeight: 600, color: 'var(--text)', marginBottom: '0.25rem' }}>{title}</div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>{desc}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EntityCreateForm onSuccess={handleEntityCreated} onCancel={() => setShowCreateForm(false)} />
          )}
        </div>
      </div>
    );
  }

  // Has entity
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

        {/* Page header */}
        <div className="page-header" style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 className="page-title">{entity.name}</h1>
            <p className="page-subtitle">{entity.entity_type} · {entity.members.length} member{entity.members.length !== 1 ? 's' : ''}</p>
          </div>

          {/* Main tabs */}
          <div style={{
            display: 'flex', background: 'var(--surface-2)',
            border: '1px solid var(--border)', borderRadius: 10, padding: '3px',
          }}>
            {(['dashboard', 'management'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setMainTab(tab)}
                style={{
                  padding: '0.375rem 0.875rem', borderRadius: 7, border: 'none', cursor: 'pointer',
                  fontSize: '0.8125rem', fontWeight: 500, transition: 'all 0.15s',
                  background: mainTab === tab ? 'var(--primary)' : 'transparent',
                  color: mainTab === tab ? '#fff' : 'var(--text-secondary)',
                  display: 'flex', alignItems: 'center', gap: '0.375rem',
                }}
              >
                {tab === 'management' && <Settings2 size={13} />}
                {tab === 'dashboard' ? 'Dashboard' : 'Management'}
              </button>
            ))}
          </div>
        </div>

        {/* ── Dashboard tab ────────────────────────────────────── */}
        {mainTab === 'dashboard' && (
          <div style={{ marginTop: '1.5rem' }}>

            {/* Dashboard controls bar */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem' }}>

              {/* View mode toggle */}
              <div style={{
                display: 'flex', background: 'var(--surface-2)',
                border: '1px solid var(--border)', borderRadius: 10, padding: '3px',
              }}>
                {(['all-time', 'monthly', 'forecast'] as const).map(mode => (
                  <button
                    key={mode}
                    onClick={() => setDashView(mode)}
                    style={{
                      padding: '0.375rem 0.875rem', borderRadius: 7, border: 'none', cursor: 'pointer',
                      fontSize: '0.8125rem', fontWeight: 500, transition: 'all 0.15s',
                      background: dashView === mode ? 'var(--primary)' : 'transparent',
                      color: dashView === mode ? '#fff' : 'var(--text-secondary)',
                      display: 'flex', alignItems: 'center', gap: '0.375rem',
                    }}
                  >
                    {mode === 'forecast' && <Activity size={13} />}
                    {mode === 'all-time' ? 'All-time' : mode === 'monthly' ? 'Monthly' : 'Forecast'}
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                {/* Currency Selector (if multiple currencies) */}
                {selectedCurrencies.length > 1 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Currency:</span>
                    <select
                      value={selectedCurrency}
                      onChange={e => setSelectedCurrency(e.target.value)}
                      className="input"
                      style={{ width: 'auto', padding: '0.375rem 0.75rem' }}
                    >
                      {selectedCurrencies.map(curr => (
                        <option key={curr} value={curr}>{curr}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Month/year selectors */}
                {dashView === 'monthly' && (
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

                {/* Admin toggle */}
                {isAdmin && (
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', userSelect: 'none' }}>
                    <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                      {includePrivate ? 'All Transactions' : 'Shared Only'}
                    </span>
                    <div
                      onClick={() => setIncludePrivate(p => !p)}
                      style={{
                        width: 40, height: 22, borderRadius: 11,
                        background: includePrivate ? 'var(--primary)' : 'var(--border)',
                        position: 'relative', transition: 'background 0.2s', cursor: 'pointer',
                      }}
                    >
                      <div style={{
                        position: 'absolute', top: 3,
                        left: includePrivate ? 21 : 3,
                        width: 16, height: 16, borderRadius: 8,
                        background: '#fff', transition: 'left 0.2s',
                      }} />
                    </div>
                  </label>
                )}

                {dashView !== 'forecast' && (
                  <button className="btn btn-ghost btn-sm" onClick={() => setRefreshTick(p => p + 1)} title="Refresh">
                    <RefreshCw size={15} />
                  </button>
                )}
              </div>
            </div>

            {/* Forecast view */}
            {dashView === 'forecast' && (
              <div className="animate-slide-up">
                <ForecastView entityId={entity.id} includePrivate={isAdmin ? includePrivate : false} currency={selectedCurrency} />
              </div>
            )}

            {/* All-time / Monthly views */}
            {dashView !== 'forecast' && (
              <>
                {summaryLoading && !summary && (
                  <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                    <div className="spinner spinner-lg" />
                  </div>
                )}

                {summary && (
                  <>
                    <div className="animate-slide-up">
                      <EntityDashboardSummary summary={summary} isAdmin={isAdmin} includePrivate={includePrivate} isMonthly={dashView === 'monthly'} />
                    </div>

                    {/* Category chart */}
                    {Object.keys(summary.categories_breakdown).length > 0 && (
                      <div className="card animate-slide-up stagger-1" style={{ marginTop: '1.25rem' }}>
                        <CategoryChart categoriesBreakdown={summary.categories_breakdown} />
                      </div>
                    )}
                  </>
                )}
              </>
            )}
          </div>
        )}

        {/* ── Management tab ───────────────────────────────────── */}
        {mainTab === 'management' && user && (
          <div style={{ marginTop: '1.5rem' }}>
            <EntityManagement
              entity={entity}
              currentUserId={user.id}
              isAdmin={isAdmin}
              onUpdate={handleEntityUpdated}
            />
          </div>
        )}
      </div>
    </div>
  );
};
