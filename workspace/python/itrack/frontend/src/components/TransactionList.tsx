import React, { useEffect, useState } from 'react';
import { Trash2, Lock, Users, ArrowUpRight, ArrowDownLeft, PiggyBank, CreditCard } from 'lucide-react';
import { Transaction } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import { entityService } from '../services/entityService';
import { useSettings } from '../contexts/SettingsContext';

interface Props {
  refreshTrigger: number;
  onUpdate: () => void;
  onDelete: () => void;
  showEntityInfo?: boolean;
  currency?: string;
  entityId?: string;
  includePrivate?: boolean;
}

type TypeFilter = 'all' | 'income' | 'expense' | 'asset' | 'liability';

const TYPE_META: Record<string, { label: string; icon: React.ReactNode; badgeClass: string; sign: string; color: string }> = {
  income:    { label: 'Income',    icon: <ArrowUpRight size={11} />,  badgeClass: 'badge badge-green', sign: '+', color: 'var(--success)' },
  expense:   { label: 'Expense',   icon: <ArrowDownLeft size={11} />, badgeClass: 'badge badge-red',   sign: '−', color: 'var(--error)' },
  asset:     { label: 'Asset',     icon: <PiggyBank size={11} />,     badgeClass: 'badge badge-blue',  sign: '+', color: '#3B82F6' },
  liability: { label: 'Liability', icon: <CreditCard size={11} />,    badgeClass: 'badge badge-orange',sign: '−', color: '#F97316' },
};

export const TransactionList: React.FC<Props> = ({
  refreshTrigger, onDelete, showEntityInfo = false, currency, entityId, includePrivate = false,
}) => {
  const { formatCurrency, formatDate } = useSettings();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<TypeFilter>('all');

  useEffect(() => { fetchTransactions(); }, [refreshTrigger, filter, currency, entityId, includePrivate]);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      if (entityId) {
        const data = await entityService.getEntityTransactions(entityId, includePrivate, currency);
        setTransactions(data);
      } else {
        const params: any = filter !== 'all' ? { type: filter } : {};
        if (currency) params.currency = currency;
        setTransactions(await transactionService.getTransactions(params));
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this transaction?')) return;
    try {
      await transactionService.deleteTransaction(id);
      onDelete();
    } catch {
      alert('Failed to delete transaction');
    }
  };

  const filtered = entityId && filter !== 'all'
    ? transactions.filter(tx => tx.type === filter)
    : transactions;

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '1.25rem 1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <h2 className="section-title" style={{ margin: 0 }}>Transaction History</h2>
        <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap' }}>
          {(['all', 'income', 'expense', 'asset', 'liability'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`filter-pill${filter === f ? ' active' : ''}${f === 'income' ? ' filter-pill-green' : ''}${f === 'expense' ? ' filter-pill-red' : ''}`}
            >
              {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner spinner-lg" />
        </div>
      )}

      {!isLoading && filtered.length === 0 && (
        <div className="empty-state"><p>No transactions found</p></div>
      )}

      {!isLoading && filtered.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table className="table-root">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                {showEntityInfo && <><th>User</th><th>Mode</th></>}
                <th>Type</th>
                <th>Currency</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'right' }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(tx => {
                const meta = TYPE_META[tx.type] ?? TYPE_META.expense;
                return (
                  <tr key={tx.id}>
                    <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap', fontSize: '0.875rem' }}>
                      {formatDate(tx.date)}
                    </td>
                    <td style={{ fontWeight: 500, maxWidth: 240 }}>
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
                        {tx.description}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-muted">{tx.category}</span>
                    </td>
                    {showEntityInfo && (
                      <>
                        <td style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                          {tx.username || 'Me'}
                        </td>
                        <td>
                          {tx.mode === 'shared' ? (
                            <span className="badge badge-blue"><Users size={11} /> Shared</span>
                          ) : (
                            <span className="badge badge-muted"><Lock size={11} /> Private</span>
                          )}
                        </td>
                      </>
                    )}
                    <td>
                      <span className={meta.badgeClass} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}>
                        {meta.icon} {meta.label}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-muted" style={{ fontSize: '0.7rem', letterSpacing: '0.04em' }}>
                        {tx.currency || 'USD'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                      <span style={{ color: meta.color }}>
                        {meta.sign}{formatCurrency(tx.amount, tx.currency || 'USD')}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {!entityId && (
                        <button
                          onClick={() => handleDelete(tx.id)}
                          className="btn btn-ghost btn-icon btn-sm"
                          title="Delete"
                          style={{ color: 'var(--error)', opacity: 0.7 }}
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
