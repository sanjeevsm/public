import React, { useState } from 'react';
import { PlusCircle, X, TrendingUp, TrendingDown, Lock, Users } from 'lucide-react';
import { TransactionInput, TransactionType, TransactionMode } from '../types/transaction';
import { transactionService } from '../services/transactionService';

interface Props {
  onSuccess: () => void;
  hasEntity?: boolean;
}

const CATEGORIES = [
  'Food & Dining','Transportation','Shopping','Entertainment',
  'Bills & Utilities','Healthcare','Education',
  'Salary','Freelance','Investment','Other',
];

export const TransactionForm: React.FC<Props> = ({ onSuccess, hasEntity = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<TransactionInput>({
    description: '', amount: 0, type: 'expense', category: '',
    date: new Date().toISOString().split('T')[0],
    mode: 'private', is_recurring: false, recurrence: undefined, recurrence_start: undefined,
  });

  const set = (patch: Partial<TransactionInput>) => setFormData(p => ({ ...p, ...patch }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await transactionService.createTransaction({
        ...formData,
        date: new Date(formData.date).toISOString(),
        recurrence: formData.is_recurring ? 'monthly' : undefined,
        recurrence_start: formData.is_recurring && formData.recurrence_start
          ? new Date(formData.recurrence_start).toISOString() : undefined,
      });
      set({ description: '', amount: 0, type: 'expense', category: '', date: new Date().toISOString().split('T')[0], mode: 'private', is_recurring: false });
      setIsOpen(false);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create transaction');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="btn btn-primary">
        <PlusCircle size={17} />
        Add Transaction
      </button>
    );
  }

  return (
    <div className="card animate-slide-up">
      {/* Card header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 className="section-title" style={{ margin: 0 }}>New Transaction</h2>
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setIsOpen(false)}>
          <X size={17} />
        </button>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Type toggle */}
        <div>
          <label className="label">Type</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {(['income', 'expense'] as TransactionType[]).map(t => (
              <button
                key={t}
                type="button"
                onClick={() => set({ type: t })}
                style={{
                  flex: 1,
                  padding: '0.625rem',
                  borderRadius: 8,
                  border: `1px solid ${formData.type === t ? 'transparent' : 'var(--border)'}`,
                  background: formData.type === t
                    ? t === 'income' ? 'var(--success-soft)' : 'var(--error-soft)'
                    : 'var(--surface)',
                  color: formData.type === t
                    ? t === 'income' ? 'var(--success)' : 'var(--error)'
                    : 'var(--text-secondary)',
                  fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
                  transition: 'all 0.15s ease',
                }}
              >
                {t === 'income' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Description + Amount on same row for wider screens */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.75rem', alignItems: 'start' }}>
          <div>
            <label className="label">Description</label>
            <input
              type="text" required
              value={formData.description}
              onChange={e => set({ description: e.target.value })}
              className="input" placeholder="What was this for?"
            />
          </div>
          <div style={{ minWidth: 130 }}>
            <label className="label">Amount</label>
            <input
              type="number" required min="0.01" step="0.01"
              value={formData.amount || ''}
              onChange={e => set({ amount: parseFloat(e.target.value) })}
              className="input" placeholder="0.00"
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div>
            <label className="label">Category</label>
            <select required value={formData.category} onChange={e => set({ category: e.target.value })} className="input">
              <option value="">Select…</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Date</label>
            <input type="date" required value={formData.date} onChange={e => set({ date: e.target.value })} className="input" />
          </div>
        </div>

        {/* Visibility (entity only) */}
        {hasEntity && (
          <div>
            <label className="label">Visibility</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {(['private', 'shared'] as TransactionMode[]).map(m => (
                <button
                  key={m}
                  type="button"
                  onClick={() => set({ mode: m })}
                  style={{
                    flex: 1, padding: '0.5rem 0.75rem', borderRadius: 8,
                    border: `1px solid ${formData.mode === m ? 'var(--primary)' : 'var(--border)'}`,
                    background: formData.mode === m ? 'var(--primary-soft)' : 'var(--surface)',
                    color: formData.mode === m ? 'var(--primary)' : 'var(--text-secondary)',
                    fontWeight: 500, fontSize: '0.875rem', cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {m === 'private' ? <Lock size={14} /> : <Users size={14} />}
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Recurring */}
        <div>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', cursor: 'pointer', userSelect: 'none' }}>
            <div
              onClick={() => set({ is_recurring: !formData.is_recurring })}
              style={{
                width: 40, height: 22, borderRadius: 99,
                background: formData.is_recurring ? 'var(--primary)' : 'var(--surface-2)',
                border: `1px solid ${formData.is_recurring ? 'var(--primary)' : 'var(--border)'}`,
                position: 'relative', transition: 'all 0.2s ease', cursor: 'pointer', flexShrink: 0,
              }}
            >
              <div style={{
                position: 'absolute', top: 2, left: formData.is_recurring ? 20 : 2,
                width: 16, height: 16, borderRadius: '50%', background: '#fff',
                transition: 'left 0.2s ease', boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
              }} />
            </div>
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text)' }}>Monthly recurring</span>
          </label>
          {formData.is_recurring && (
            <div style={{ marginTop: '0.625rem' }}>
              <label className="label">Recurrence start</label>
              <input
                type="date"
                value={formData.recurrence_start || new Date().toISOString().split('T')[0]}
                onChange={e => set({ recurrence_start: e.target.value })}
                className="input"
              />
            </div>
          )}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '0.625rem', paddingTop: '0.5rem' }}>
          <button type="submit" disabled={isLoading} className="btn btn-primary" style={{ flex: 1 }}>
            {isLoading ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Adding…</> : 'Add Transaction'}
          </button>
          <button type="button" onClick={() => setIsOpen(false)} className="btn btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
