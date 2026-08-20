import React, { useEffect, useMemo, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { ArrowRight, Info, TrendingDown, TrendingUp } from 'lucide-react';
import { transactionService } from '../services/transactionService';
import { entityService } from '../services/entityService';
import { MonthlyDataPoint, RecurringTransaction } from '../types/transaction';
import { useSettings } from '../contexts/SettingsContext';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend, Filler);

const MO = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// Least-squares linear slope ($ change per period)
function slope(vals: number[]): number {
  const n = vals.length;
  if (n < 2) return 0;
  const mx = (n - 1) / 2;
  const my = vals.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  vals.forEach((y, x) => { num += (x - mx) * (y - my); den += (x - mx) ** 2; });
  return den === 0 ? 0 : num / den;
}

// Convert a percentage to a monthly compound rate
// yearly 5% → (1.05)^(1/12) - 1 ≈ 0.00407;  monthly 5% → 0.05
function toMonthlyRate(pct: number, period: 'monthly' | 'yearly'): number {
  const r = pct / 100;
  return period === 'yearly' ? Math.pow(1 + r, 1 / 12) - 1 : r;
}

interface ForecastPoint {
  label: string;
  optimistic: number;
  base: number;
  pessimistic: number;
  // Monthly figures per scenario (absent for the starting-balance row)
  baseIncome?: number;
  baseExpense?: number;
  optIncome?: number;
  optExpense?: number;
  pessIncome?: number;
  pessExpense?: number;
}

interface Assumptions {
  baselineIncome: number;
  baselineExpense: number;
  incomeSlope: number;
  expenseSlope: number;
  monthsForward: number;
}

function buildForecast(
  currentBalance: number,
  history: MonthlyDataPoint[],
  targetYear: number,
  targetMonth: number,
  incomeRate: number,
  expenseRate: number,
  recurringTxs: RecurringTransaction[] = [],
): { points: ForecastPoint[]; assumptions: Assumptions } {
  const EMPTY = {
    points: [],
    assumptions: { baselineIncome: 0, baselineExpense: 0, incomeSlope: 0, expenseSlope: 0, monthsForward: 0 },
  };
  if (!history.length || !targetYear || !targetMonth) return EMPTY;

  const now = new Date();
  const nowY = now.getFullYear();
  const nowM = now.getMonth() + 1;
  const monthsForward = (targetYear - nowY) * 12 + (targetMonth - nowM);
  if (monthsForward <= 0) return EMPTY;

  // Calculate baseline from average of all history (not just last month which might be zero)
  const activeHistory = history.filter(d => d.income > 0 || d.expense > 0);

  // If history is too sparse, use recurring transactions to calculate baseline
  let baselineIncome = 0;
  let baselineExpense = 0;

  if (activeHistory.length >= 2) {
    // Good history - use average
    const totalIncome = history.reduce((sum, d) => sum + d.income, 0);
    const totalExpense = history.reduce((sum, d) => sum + d.expense, 0);
    baselineIncome = totalIncome / history.length;
    baselineExpense = totalExpense / history.length;
  } else {
    // Sparse or no history - calculate from recurring transactions
    for (const tx of recurringTxs) {
      if (tx.type === 'income') {
        baselineIncome += tx.amount;
      } else if (tx.type === 'expense') {
        baselineExpense += tx.amount;
      }
    }
  }

  const last = history[history.length - 1];
  const baselineTm = last.year * 12 + (last.month - 1);

  const hasEnoughForSlope = activeHistory.length >= 2;
  const incomeSlope  = hasEnoughForSlope ? slope(activeHistory.map(d => d.income))  : 0;
  const expenseSlope = hasEnoughForSlope ? slope(activeHistory.map(d => d.expense)) : 0;

  // Pre-process recurring transactions: include all that are already active or will start during forecast.
  // Each carries a tm (year*12 + month-1) marking when it starts.
  // Separate already-active from future ones
  const nowTm = now.getFullYear() * 12 + now.getMonth();

  const alreadyActiveRecurring = recurringTxs
    .filter(tx => tx.recurrence_start != null)
    .map(tx => {
      const d = new Date(tx.recurrence_start!);
      const tm = d.getFullYear() * 12 + d.getMonth();
      return { ...tx, tm };
    })
    .filter(tx => tx.tm <= nowTm); // Already active

  const futureRecurring = recurringTxs
    .filter(tx => tx.recurrence_start != null)
    .map(tx => {
      const d = new Date(tx.recurrence_start!);
      const tm = d.getFullYear() * 12 + d.getMonth();
      return { ...tx, tm };
    })
    .filter(tx => tx.tm > nowTm && tx.tm <= baselineTm + monthsForward); // Starts in future during forecast

  // If history is sparse, use already-active recurring as baseline
  if (activeHistory.length < 2 && alreadyActiveRecurring.length > 0) {
    baselineIncome = 0;
    baselineExpense = 0;
    for (const tx of alreadyActiveRecurring) {
      if (tx.type === 'income') {
        baselineIncome += tx.amount;
      } else if (tx.type === 'expense') {
        baselineExpense += tx.amount;
      }
    }
  }

  const points: ForecastPoint[] = [{
    label: `${MO[nowM - 1]} '${String(nowY).slice(2)}`,
    optimistic: currentBalance,
    base: currentBalance,
    pessimistic: currentBalance,
  }];

  let bOpt = currentBalance, bBase = currentBalance, bPess = currentBalance;

  for (let i = 1; i <= monthsForward; i++) {
    const pTm = nowY * 12 + (nowM - 1) + i;
    const pY = Math.floor(pTm / 12);
    const pM = (pTm % 12) + 1;

    // Sum up monthly amounts from NEW recurring transactions (future ones) active by this month
    let extraIncome = 0, extraExpense = 0;
    for (const tx of futureRecurring) {
      if (tx.tm <= pTm) {
        if (tx.type === 'income') extraIncome += tx.amount;
        else if (tx.type === 'expense') extraExpense += tx.amount;
      }
    }

    // Base: flat baseline + any new recurring contributions
    bBase += (baselineIncome + extraIncome) - (baselineExpense + extraExpense);

    // Optimistic: baseline grows/shrinks by compound rate; new recurring added at face value
    const iOpt  = baselineIncome  * (1 + incomeRate)  ** i + extraIncome;
    const eOpt  = Math.max(0, baselineExpense * (1 - expenseRate) ** i) + extraExpense;
    bOpt += iOpt - eOpt;

    // Pessimistic: baseline shrinks/grows by compound rate; new recurring added at face value
    const iPess = Math.max(0, baselineIncome * (1 - incomeRate)  ** i) + extraIncome;
    const ePess = baselineExpense * (1 + expenseRate) ** i + extraExpense;
    bPess += iPess - ePess;

    points.push({
      label: `${MO[pM - 1]} '${String(pY).slice(2)}`,
      optimistic:   +(bOpt.toFixed(2)),
      base:         +(bBase.toFixed(2)),
      pessimistic:  +(bPess.toFixed(2)),
      baseIncome:   +(( baselineIncome + extraIncome).toFixed(2)),
      baseExpense:  +(( baselineExpense + extraExpense).toFixed(2)),
      optIncome:    +(iOpt.toFixed(2)),
      optExpense:   +(eOpt.toFixed(2)),
      pessIncome:   +(iPess.toFixed(2)),
      pessExpense:  +(ePess.toFixed(2)),
    });
  }

  return { points, assumptions: { baselineIncome, baselineExpense, incomeSlope, expenseSlope, monthsForward } };
}

// ─── Table style helpers ────────────────────────────────────────────────────

function thStyle(align: 'left' | 'right', color?: string): React.CSSProperties {
  return {
    padding: '0.5rem 0.75rem',
    textAlign: align,
    fontWeight: 600,
    fontSize: '0.6875rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: color ?? 'var(--text-muted)',
    whiteSpace: 'nowrap',
  };
}

function tdStyle(align: 'left' | 'right', bold?: boolean): React.CSSProperties {
  return {
    padding: '0.45rem 0.75rem',
    textAlign: align,
    fontWeight: bold ? 600 : 400,
    color: 'var(--text)',
    whiteSpace: 'nowrap',
    borderBottom: '1px solid var(--border)',
  };
}

// ─── Component ─────────────────────────────────────────────────────────────

const C = { optimistic: '#22c55e', base: '#6366f1', pessimistic: '#f43f5e' };

interface ForecastViewProps {
  entityId?: string;
  includePrivate?: boolean;
  currency?: string;
}

export const ForecastView: React.FC<ForecastViewProps> = ({ entityId, includePrivate = false, currency: initialCurrency = 'USD' }) => {
  const { formatCurrency, selectedCurrencies } = useSettings();
  const [selectedForecastCurrency, setSelectedForecastCurrency] = useState(initialCurrency);
  const fmt = (n: number) => formatCurrency(n, false);
  const fmtDelta = (n: number) => `${n >= 0 ? '+' : ''}${fmt(n)}`;

  // Update selected currency when prop changes
  useEffect(() => {
    setSelectedForecastCurrency(initialCurrency);
  }, [initialCurrency]);

  const now = new Date();
  const pad = (x: number) => String(x).padStart(2, '0');

  const defaultTarget = new Date(now.getFullYear(), now.getMonth() + 6);
  const defaultTargetStr = `${defaultTarget.getFullYear()}-${pad(defaultTarget.getMonth() + 1)}`;
  const minDate = (() => {
    const d = new Date(now.getFullYear(), now.getMonth() + 1);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}`;
  })();
  const maxDate = `${now.getFullYear() + 5}-${pad(now.getMonth() + 1)}`;

  const [history, setHistory] = useState<MonthlyDataPoint[]>([]);
  const [recurringTxs, setRecurringTxs] = useState<RecurringTransaction[]>([]);
  const [currentBalance, setCurrentBalance] = useState(0);
  const [historyMonths, setHistoryMonths] = useState(6);
  const [targetDate, setTargetDate] = useState(defaultTargetStr);
  const [incomeChangePct, setIncomeChangePct] = useState(5);
  const [expenseChangePct, setExpenseChangePct] = useState(5);
  const [deviationPeriod, setDeviationPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        if (entityId) {
          const [summary, hist, recurring] = await Promise.all([
            entityService.getEntitySummary(entityId, includePrivate),
            entityService.getEntityHistory(entityId, historyMonths, includePrivate, selectedForecastCurrency),
            entityService.getEntityRecurringTransactions(entityId, includePrivate, selectedForecastCurrency),
          ]);
          if (!cancelled) {
            setCurrentBalance(summary.total_balance);
            setHistory(hist);
            setRecurringTxs(recurring);
          }
        } else {
          const [summary, hist, recurring] = await Promise.all([
            transactionService.getSummary(selectedForecastCurrency),
            transactionService.getMonthlyHistory(historyMonths, selectedForecastCurrency),
            transactionService.getRecurringTransactions(selectedForecastCurrency),
          ]);
          if (!cancelled) {
            setCurrentBalance(summary.total_balance);
            setHistory(hist);
            setRecurringTxs(recurring);
          }
        }
      } catch {
        if (!cancelled) setError('Failed to load forecast data. Make sure transactions exist.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [historyMonths, entityId, includePrivate, selectedForecastCurrency]);

  const [targetYear, targetMonth] = useMemo(() => {
    if (!targetDate) return [0, 0];
    return targetDate.split('-').map(Number);
  }, [targetDate]);

  const { points, assumptions } = useMemo(() => {
    // Debug logging
    console.log('Forecast Input:', {
      currency: selectedForecastCurrency,
      recurringCount: recurringTxs.length,
      recurring: recurringTxs.map(tx => ({ type: tx.type, amount: tx.amount, desc: tx.description })),
    });
    return buildForecast(
      currentBalance, history, targetYear, targetMonth,
      toMonthlyRate(incomeChangePct, deviationPeriod),
      toMonthlyRate(expenseChangePct, deviationPeriod),
      recurringTxs,
    );
  }, [currentBalance, history, targetYear, targetMonth, incomeChangePct, expenseChangePct, deviationPeriod, recurringTxs, selectedForecastCurrency]);

  const last = points.length > 1 ? points[points.length - 1] : null;
  const hasData = points.length > 1;
  const manyPoints = points.length > 18;

  const pLabel = deviationPeriod === 'monthly' ? 'mo' : 'yr';

  const chartData = useMemo(() => ({
    labels: points.map(p => p.label),
    datasets: [
      {
        label: `Optimistic (inc +${incomeChangePct}%, exp −${expenseChangePct}%/${pLabel})`,
        data: points.map(p => p.optimistic),
        borderColor: C.optimistic,
        borderWidth: 2,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
      {
        label: 'Base (no change)',
        data: points.map(p => p.base),
        borderColor: C.base,
        borderWidth: 2.5,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
      {
        label: `Pessimistic (inc −${incomeChangePct}%, exp +${expenseChangePct}%/${pLabel})`,
        data: points.map(p => p.pessimistic),
        borderColor: C.pessimistic,
        borderWidth: 2,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
    ],
  }), [points, incomeChangePct, expenseChangePct, pLabel, manyPoints]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 500 },
    interaction: { mode: 'index' as const, intersect: false },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#888',
          usePointStyle: true,
          pointStyleWidth: 8,
          font: { size: 12 },
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(13,17,23,0.96)',
        borderColor: 'rgba(255,255,255,0.10)',
        borderWidth: 1,
        titleColor: '#e6edf3',
        bodyColor: '#8b949e',
        padding: 12,
        callbacks: {
          label: (ctx: any) => ` ${ctx.dataset.label.split(' (')[0]}: ${fmt(ctx.parsed.y)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(128,128,128,0.07)' },
        ticks: { color: '#666', maxTicksLimit: 12, font: { size: 11 } },
      },
      y: {
        grid: { color: 'rgba(128,128,128,0.07)' },
        ticks: {
          color: '#666',
          font: { size: 11 },
          maxTicksLimit: 7,
          callback: (v: any) => fmt(v),
        },
      },
    },
  }), [fmt]);

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <div className="spinner spinner-lg" />
    </div>
  );

  if (error) return (
    <div className="alert alert-error" style={{ marginTop: '0.5rem' }}>{error}</div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

      {/* ── Controls ─────────────────────────────────────────────── */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'flex-end' }}>

          {/* Currency Selector (show if multiple currencies available) */}
          {selectedCurrencies.length > 1 && (
            <div>
              <label className="label">Forecast Currency</label>
              <select
                value={selectedForecastCurrency}
                onChange={(e) => setSelectedForecastCurrency(e.target.value)}
                className="input"
                style={{ width: 'auto', minWidth: 100 }}
              >
                {selectedCurrencies.map(curr => (
                  <option key={curr} value={curr}>{curr}</option>
                ))}
              </select>
            </div>
          )}

          {/* Target date */}
          <div>
            <label className="label">Forecast until</label>
            <input
              type="month"
              value={targetDate}
              min={minDate}
              max={maxDate}
              onChange={e => setTargetDate(e.target.value)}
              className="input"
              style={{ width: 'auto' }}
            />
          </div>

          {/* History window */}
          <div>
            <label className="label">History window</label>
            <div style={{
              display: 'flex', background: 'var(--surface-2)',
              border: '1px solid var(--border)', borderRadius: 8, padding: 2,
            }}>
              {[3, 6, 12].map(m => (
                <button
                  key={m}
                  onClick={() => setHistoryMonths(m)}
                  style={{
                    padding: '0.3rem 0.75rem', borderRadius: 6, border: 'none', cursor: 'pointer',
                    fontSize: '0.8125rem', fontWeight: 500, transition: 'all 0.15s',
                    background: historyMonths === m ? 'var(--primary)' : 'transparent',
                    color: historyMonths === m ? '#fff' : 'var(--text-secondary)',
                  }}
                >
                  {m}mo
                </button>
              ))}
            </div>
          </div>

          {/* Deviation period toggle */}
          <div>
            <label className="label">Deviation per</label>
            <div style={{
              display: 'flex', background: 'var(--surface-2)',
              border: '1px solid var(--border)', borderRadius: 8, padding: 2,
            }}>
              {(['monthly', 'yearly'] as const).map(p => (
                <button
                  key={p}
                  onClick={() => setDeviationPeriod(p)}
                  style={{
                    padding: '0.3rem 0.75rem', borderRadius: 6, border: 'none', cursor: 'pointer',
                    fontSize: '0.8125rem', fontWeight: 500, transition: 'all 0.15s',
                    background: deviationPeriod === p ? 'var(--primary)' : 'transparent',
                    color: deviationPeriod === p ? '#fff' : 'var(--text-secondary)',
                  }}
                >
                  {p === 'monthly' ? 'Monthly' : 'Yearly'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Sliders row */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', marginTop: '0.75rem' }}>
          {/* Income change slider */}
          <div style={{ flex: 1, minWidth: 220 }}>
            <label className="label">
              Income change:{' '}
              <strong style={{ color: C.optimistic }}>{incomeChangePct}% / {pLabel}</strong>
            </label>
            <input
              type="range"
              min={0}
              max={20}
              step={1}
              value={incomeChangePct}
              onChange={e => setIncomeChangePct(+e.target.value)}
              style={{ width: '100%', accentColor: C.optimistic, marginBottom: 4 }}
            />
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: '0.6875rem', color: 'var(--text-muted)',
            }}>
              <span style={{ color: C.optimistic }}>Opt: +{incomeChangePct}%/{pLabel}</span>
              <span>Base: no change</span>
              <span style={{ color: C.pessimistic }}>Pess: −{incomeChangePct}%/{pLabel}</span>
            </div>
          </div>

          {/* Expense change slider */}
          <div style={{ flex: 1, minWidth: 220 }}>
            <label className="label">
              Expense change:{' '}
              <strong style={{ color: C.pessimistic }}>{expenseChangePct}% / {pLabel}</strong>
            </label>
            <input
              type="range"
              min={0}
              max={20}
              step={1}
              value={expenseChangePct}
              onChange={e => setExpenseChangePct(+e.target.value)}
              style={{ width: '100%', accentColor: C.pessimistic, marginBottom: 4 }}
            />
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: '0.6875rem', color: 'var(--text-muted)',
            }}>
              <span style={{ color: C.optimistic }}>Opt: −{expenseChangePct}%/{pLabel}</span>
              <span>Base: no change</span>
              <span style={{ color: C.pessimistic }}>Pess: +{expenseChangePct}%/{pLabel}</span>
            </div>
          </div>
        </div>
      </div>

      {hasData ? (
        <>
          {/* ── Line chart ──────────────────────────────────────── */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h2 className="section-title" style={{ marginBottom: '1rem' }}>
              Projected Net Balance
            </h2>
            <div style={{ height: 300 }}>
              <Line data={chartData} options={chartOptions as any} />
            </div>
          </div>

          {/* ── At-target cards ─────────────────────────────────── */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}>
            {([
              { key: 'optimistic'  as const, label: 'Optimistic', desc: `Inc +${incomeChangePct}%, Exp −${expenseChangePct}%/${pLabel}`, color: C.optimistic, Icon: TrendingDown },
              { key: 'base'        as const, label: 'Base',        desc: 'No change in current scenario',                              color: C.base,       Icon: ArrowRight  },
              { key: 'pessimistic' as const, label: 'Pessimistic', desc: `Inc −${incomeChangePct}%, Exp +${expenseChangePct}%/${pLabel}`, color: C.pessimistic, Icon: TrendingUp  },
            ] as const).map(({ key, label, desc, color, Icon }) => {
              const val = last?.[key] ?? 0;
              return (
                <div
                  key={key}
                  className="stat-card"
                  style={{ '--accent-gradient': `linear-gradient(135deg, ${color}, ${color}66)` } as React.CSSProperties}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{label}</span>
                    <div style={{ width: 34, height: 34, borderRadius: 8, background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>
                      <Icon size={16} strokeWidth={2} />
                    </div>
                  </div>
                  <div className="stat-value" style={{ color: val >= 0 ? 'var(--success)' : 'var(--error)' }}>
                    {fmt(val)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>{desc}</div>
                </div>
              );
            })}
          </div>

          {/* ── Monthly breakdown table ─────────────────────────── */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <h2 className="section-title" style={{ marginBottom: '1rem' }}>Monthly Projection Breakdown</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    {/* Base scenario columns */}
                    <th style={thStyle('left')}>Month</th>
                    <th style={thStyle('right', C.base)}>Income</th>
                    <th style={thStyle('right', C.base)}>Expense</th>
                    <th style={thStyle('right', C.base)}>Net/mo</th>
                    <th style={thStyle('right', C.base)}>Balance</th>
                    {/* Separator */}
                    <th style={{ width: 1, background: 'var(--border)', padding: 0 }} />
                    {/* Optimistic */}
                    <th style={thStyle('right', C.optimistic)}>Opt Income</th>
                    <th style={thStyle('right', C.optimistic)}>Opt Expense</th>
                    <th style={thStyle('right', C.optimistic)}>Opt Balance</th>
                    {/* Separator */}
                    <th style={{ width: 1, background: 'var(--border)', padding: 0 }} />
                    {/* Pessimistic */}
                    <th style={thStyle('right', C.pessimistic)}>Pess Income</th>
                    <th style={thStyle('right', C.pessimistic)}>Pess Expense</th>
                    <th style={thStyle('right', C.pessimistic)}>Pess Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {points.map((p, idx) => {
                    const isStart = idx === 0;
                    const baseNet = p.baseIncome != null && p.baseExpense != null
                      ? p.baseIncome - p.baseExpense : null;
                    const rowBg = idx % 2 === 0 ? 'var(--surface)' : 'var(--surface-2)';
                    return (
                      <tr key={p.label} style={{ background: rowBg }}>
                        <td style={tdStyle('left', true)}>{p.label}</td>
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.baseIncome!)}</td>
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.baseExpense!)}</td>
                        <td style={tdStyle('right')}>
                          {isStart ? '—' : (
                            <span style={{ color: baseNet! >= 0 ? 'var(--success)' : 'var(--error)', fontWeight: 600 }}>
                              {baseNet! >= 0 ? '+' : ''}{fmt(baseNet!)}
                            </span>
                          )}
                        </td>
                        <td style={{ ...tdStyle('right'), fontWeight: 700, color: p.base >= 0 ? 'var(--success)' : 'var(--error)' }}>
                          {fmt(p.base)}
                        </td>
                        <td style={{ width: 1, background: 'var(--border)', padding: 0 }} />
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.optIncome!)}</td>
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.optExpense!)}</td>
                        <td style={{ ...tdStyle('right'), fontWeight: 700, color: p.optimistic >= 0 ? 'var(--success)' : 'var(--error)' }}>
                          {fmt(p.optimistic)}
                        </td>
                        <td style={{ width: 1, background: 'var(--border)', padding: 0 }} />
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.pessIncome!)}</td>
                        <td style={tdStyle('right')}>{isStart ? '—' : fmt(p.pessExpense!)}</td>
                        <td style={{ ...tdStyle('right'), fontWeight: 700, color: p.pessimistic >= 0 ? 'var(--success)' : 'var(--error)' }}>
                          {fmt(p.pessimistic)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* ── Assumptions ─────────────────────────────────────── */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
              <Info size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              <span className="section-title" style={{ margin: 0 }}>Forecast Assumptions</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(155px, 1fr))', gap: '0.625rem' }}>
              {[
                { label: 'Starting balance',      value: fmt(currentBalance) },
                { label: 'Monthly income (base)', value: fmt(assumptions.baselineIncome),  sub: `trend: ${fmtDelta(assumptions.incomeSlope)}/mo` },
                { label: 'Monthly expense (base)',value: fmt(assumptions.baselineExpense), sub: `trend: ${fmtDelta(assumptions.expenseSlope)}/mo` },
                { label: 'History used',          value: `${historyMonths} months` },
                { label: 'Months projected',      value: String(assumptions.monthsForward) },
              ].map(item => (
                <div key={item.label} style={{ background: 'var(--surface-2)', borderRadius: 8, padding: '0.625rem 0.875rem', display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
                  <span style={{ fontSize: '0.6875rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
                    {item.label}
                  </span>
                  <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '0.9375rem' }}>{item.value}</span>
                  {item.sub && <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{item.sub}</span>}
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>Select a future target date above to generate your balance forecast.</p>
        </div>
      )}
    </div>
  );
};

export default ForecastView;
