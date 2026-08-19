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
import { MonthlyDataPoint } from '../types/transaction';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend, Filler);

const MO = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

const fmt = (n: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);

const fmtDelta = (n: number) =>
  `${n >= 0 ? '+' : ''}${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)}`;

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

interface ForecastPoint {
  label: string;
  optimistic: number;
  base: number;
  pessimistic: number;
}

interface Assumptions {
  avgIncome: number;
  avgExpense: number;
  incomeSlope: number;
  expenseSlope: number;
  monthsForward: number;
}

function buildForecast(
  currentBalance: number,
  history: MonthlyDataPoint[],
  targetYear: number,
  targetMonth: number,
  expenseRate: number,  // fraction/month for pessimistic/optimistic compound change
): { points: ForecastPoint[]; assumptions: Assumptions } {
  const EMPTY = {
    points: [],
    assumptions: { avgIncome: 0, avgExpense: 0, incomeSlope: 0, expenseSlope: 0, monthsForward: 0 },
  };
  if (!history.length || !targetYear || !targetMonth) return EMPTY;

  const n = history.length;
  const avgIncome  = history.reduce((s, d) => s + d.income,  0) / n;
  const avgExpense = history.reduce((s, d) => s + d.expense, 0) / n;
  const incomeSlope  = slope(history.map(d => d.income));
  const expenseSlope = slope(history.map(d => d.expense));

  const now = new Date();
  const nowY = now.getFullYear();
  const nowM = now.getMonth() + 1;
  const monthsForward = (targetYear - nowY) * 12 + (targetMonth - nowM);
  if (monthsForward <= 0) return EMPTY;

  // Starting point = current balance
  const points: ForecastPoint[] = [{
    label: `${MO[nowM - 1]} '${String(nowY).slice(2)}`,
    optimistic: currentBalance,
    base: currentBalance,
    pessimistic: currentBalance,
  }];

  let bOpt = currentBalance, bBase = currentBalance, bPess = currentBalance;

  for (let i = 1; i <= monthsForward; i++) {
    const tm = nowY * 12 + (nowM - 1) + i;
    const pY = Math.floor(tm / 12);
    const pM = (tm % 12) + 1;

    // Income: linear projection (same across all 3 scenarios)
    const income = Math.max(0, avgIncome + incomeSlope * i);

    // Expense scenarios
    const eBase = Math.max(0, avgExpense + expenseSlope * i);           // follows historical trend
    const eOpt  = Math.max(0, avgExpense * (1 - expenseRate) ** i);     // compound decrease
    const ePess = avgExpense * (1 + expenseRate) ** i;                  // compound increase

    bOpt  += income - eOpt;
    bBase += income - eBase;
    bPess += income - ePess;

    points.push({
      label: `${MO[pM - 1]} '${String(pY).slice(2)}`,
      optimistic:  +(bOpt.toFixed(2)),
      base:        +(bBase.toFixed(2)),
      pessimistic: +(bPess.toFixed(2)),
    });
  }

  return { points, assumptions: { avgIncome, avgExpense, incomeSlope, expenseSlope, monthsForward } };
}

// ─── Component ─────────────────────────────────────────────────────────────

const C = { optimistic: '#22c55e', base: '#6366f1', pessimistic: '#f43f5e' };

export const ForecastView: React.FC = () => {
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
  const [currentBalance, setCurrentBalance] = useState(0);
  const [historyMonths, setHistoryMonths] = useState(6);
  const [targetDate, setTargetDate] = useState(defaultTargetStr);
  const [expenseChangePct, setExpenseChangePct] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const [summary, hist] = await Promise.all([
          transactionService.getSummary(),
          transactionService.getMonthlyHistory(historyMonths),
        ]);
        if (!cancelled) {
          setCurrentBalance(summary.total_balance);
          setHistory(hist);
        }
      } catch {
        if (!cancelled) setError('Failed to load forecast data. Make sure transactions exist.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [historyMonths]);

  const [targetYear, targetMonth] = useMemo(() => {
    if (!targetDate) return [0, 0];
    return targetDate.split('-').map(Number);
  }, [targetDate]);

  const { points, assumptions } = useMemo(
    () => buildForecast(currentBalance, history, targetYear, targetMonth, expenseChangePct / 100),
    [currentBalance, history, targetYear, targetMonth, expenseChangePct],
  );

  const last = points.length > 1 ? points[points.length - 1] : null;
  const hasData = points.length > 1;
  const manyPoints = points.length > 18;

  const chartData = useMemo(() => ({
    labels: points.map(p => p.label),
    datasets: [
      {
        label: `Optimistic (−${expenseChangePct}%/mo)`,
        data: points.map(p => p.optimistic),
        borderColor: C.optimistic,
        borderWidth: 2,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
      {
        label: 'Base (historical trend)',
        data: points.map(p => p.base),
        borderColor: C.base,
        borderWidth: 2.5,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
      {
        label: `Pessimistic (+${expenseChangePct}%/mo)`,
        data: points.map(p => p.pessimistic),
        borderColor: C.pessimistic,
        borderWidth: 2,
        pointRadius: manyPoints ? 0 : 3,
        fill: false,
        tension: 0.35,
      },
    ],
  }), [points, expenseChangePct, manyPoints]);

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
  }), []);

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

          {/* Scenario deviation slider */}
          <div style={{ flex: 1, minWidth: 240 }}>
            <label className="label">
              Scenario deviation:{' '}
              <strong style={{ color: 'var(--primary)' }}>{expenseChangePct}% / month</strong>
            </label>
            <input
              type="range"
              min={1}
              max={20}
              step={1}
              value={expenseChangePct}
              onChange={e => setExpenseChangePct(+e.target.value)}
              style={{ width: '100%', accentColor: 'var(--primary)', marginBottom: 4 }}
            />
            <div style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: '0.6875rem', color: 'var(--text-muted)',
            }}>
              <span style={{ color: C.optimistic }}>Optimistic −{expenseChangePct}%/mo</span>
              <span style={{ color: 'var(--text-muted)' }}>Base = trend</span>
              <span style={{ color: C.pessimistic }}>Pessimistic +{expenseChangePct}%/mo</span>
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
              {
                key: 'optimistic' as const,
                label: 'Optimistic',
                desc: `Expenses shrink ${expenseChangePct}%/mo`,
                color: C.optimistic,
                Icon: TrendingDown,
              },
              {
                key: 'base' as const,
                label: 'Base (Trend)',
                desc: 'Follows historical pattern',
                color: C.base,
                Icon: ArrowRight,
              },
              {
                key: 'pessimistic' as const,
                label: 'Pessimistic',
                desc: `Expenses grow ${expenseChangePct}%/mo`,
                color: C.pessimistic,
                Icon: TrendingUp,
              },
            ] as const).map(({ key, label, desc, color, Icon }) => {
              const val = last?.[key] ?? 0;
              const positive = val >= 0;
              return (
                <div
                  key={key}
                  className="stat-card"
                  style={{ '--accent-gradient': `linear-gradient(135deg, ${color}, ${color}66)` } as React.CSSProperties}
                >
                  <div style={{
                    display: 'flex', justifyContent: 'space-between',
                    alignItems: 'center', marginBottom: '0.75rem',
                  }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
                      {label}
                    </span>
                    <div style={{
                      width: 34, height: 34, borderRadius: 8,
                      background: `${color}18`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color,
                    }}>
                      <Icon size={16} strokeWidth={2} />
                    </div>
                  </div>
                  <div className="stat-value" style={{ color: positive ? 'var(--success)' : 'var(--error)' }}>
                    {fmt(val)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>
                    {desc}
                  </div>
                </div>
              );
            })}
          </div>

          {/* ── Assumptions ─────────────────────────────────────── */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem',
            }}>
              <Info size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              <span className="section-title" style={{ margin: 0 }}>Forecast Assumptions</span>
            </div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(155px, 1fr))',
              gap: '0.625rem',
            }}>
              {[
                { label: 'Starting balance',    value: fmt(currentBalance) },
                {
                  label: 'Avg monthly income',
                  value: fmt(assumptions.avgIncome),
                  sub: `trend: ${fmtDelta(assumptions.incomeSlope)}/mo`,
                },
                {
                  label: 'Avg monthly expense',
                  value: fmt(assumptions.avgExpense),
                  sub: `trend: ${fmtDelta(assumptions.expenseSlope)}/mo`,
                },
                { label: 'History used',        value: `${historyMonths} months` },
                { label: 'Months projected',    value: String(assumptions.monthsForward) },
              ].map(item => (
                <div
                  key={item.label}
                  style={{
                    background: 'var(--surface-2)', borderRadius: 8,
                    padding: '0.625rem 0.875rem',
                    display: 'flex', flexDirection: 'column', gap: '0.125rem',
                  }}
                >
                  <span style={{
                    fontSize: '0.6875rem', fontWeight: 600,
                    textTransform: 'uppercase', letterSpacing: '0.06em',
                    color: 'var(--text-muted)',
                  }}>
                    {item.label}
                  </span>
                  <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '0.9375rem' }}>
                    {item.value}
                  </span>
                  {item.sub && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                      {item.sub}
                    </span>
                  )}
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
