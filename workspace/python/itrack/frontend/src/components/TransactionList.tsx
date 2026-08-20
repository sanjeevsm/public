import React, { useEffect, useState } from 'react';
import { Trash2, Lock, Users, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { Transaction } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import { format } from 'date-fns';
import { useSettings } from '../contexts/SettingsContext';

interface Props {
  refreshTrigger: number;
  onUpdate: () => void;
  onDelete: () => void;
  showEntityInfo?: boolean;
}

export const TransactionList: React.FC<Props> = ({ refreshTrigger, onDelete, showEntityInfo = false }) => {
  const { formatCurrency } = useSettings();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => { fetchTransactions(); }, [refreshTrigger, filter]);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      const params = filter !== 'all' ? { type: filter } : {};
      setTransactions(await transactionService.getTransactions(params));
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

  const fmt = (n: number) => formatCurrency(n, false);

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '1.25rem 1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <h2 className="section-title" style={{ margin: 0 }}>Transaction History</h2>
        <div style={{ display: 'flex', gap: '0.375rem' }}>
          {(['all', 'income', 'expense'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`filter-pill${filter === f ? ' active' : ''}${f === 'income' ? ' filter-pill-green' : ''}${f === 'expense' ? ' filter-pill-red' : ''}`}
            >
              {f === 'all' ? 'All' : f === 'income' ? 'Income' : 'Expenses'}
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner spinner-lg" />
        </div>
      )}

      {/* Empty */}
      {!isLoading && transactions.length === 0 && (
        <div className="empty-state">
          <p>No transactions found</p>
        </div>
      )}

      {/* Table */}
      {!isLoading && transactions.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table className="table-root">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                {showEntityInfo && <><th>User</th><th>Mode</th></>}
                <th>Type</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'right' }}></th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => (
                <tr key={tx.id}>
                  <td style={{ color: 'var(--text-secondary)', whiteSpace: 'nowrap', fontSize: '0.875rem' }}>
                    {format(new Date(tx.date), 'MMM dd, yyyy')}
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
                        {tx.username || 'Unknown'}
                      </td>
                      <td>
                        {tx.mode === 'shared' ? (
                          <span className="badge badge-blue">
                            <Users size={11} /> Shared
                          </span>
                        ) : (
                          <span className="badge badge-muted">
                            <Lock size={11} /> Private
                          </span>
                        )}
                      </td>
                    </>
                  )}
                  <td>
                    {tx.type === 'income' ? (
                      <span className="badge badge-green">
                        <ArrowUpRight size={11} /> Income
                      </span>
                    ) : (
                      <span className="badge badge-red">
                        <ArrowDownLeft size={11} /> Expense
                      </span>
                    )}
                  </td>
                  <td style={{ textAlign: 'right', whiteSpace: 'nowrap', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                    <span style={{ color: tx.type === 'income' ? 'var(--success)' : 'var(--error)' }}>
                      {tx.type === 'income' ? '+' : '−'}{fmt(tx.amount)}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      onClick={() => handleDelete(tx.id)}
                      className="btn btn-ghost btn-icon btn-sm"
                      title="Delete"
                      style={{ color: 'var(--error)', opacity: 0.7 }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
