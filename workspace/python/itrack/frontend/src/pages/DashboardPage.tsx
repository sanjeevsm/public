import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { TransactionSummary } from '../types/transaction';
import { transactionService } from '../services/transactionService';
import { DashboardSummary } from '../components/DashboardSummary';
import { TransactionList } from '../components/TransactionList';
import { TransactionForm } from '../components/TransactionForm';
import { ImportExport } from '../components/ImportExport';
import { CategoryChart } from '../components/CategoryChart';
import { EntityStatusBanner } from '../components/EntityStatusBanner';
import { useAuth } from '../contexts/AuthContext';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [viewMonthly, setViewMonthly] = useState(false);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    fetchSummary();
  }, [refreshTrigger]);

  const fetchSummary = async () => {
    setIsLoading(true);
    try {
      const data = viewMonthly
        ? await transactionService.getMonthlySummary(selectedYear, selectedMonth)
        : await transactionService.getSummary();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  if (isLoading) {
    return (
      <>
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            Financial Dashboard
          </h1>

          {/* Entity Status Banner */}
          <EntityStatusBanner hasEntity={!!user?.entity_id} />

          {/* Summary Cards */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2">
                <input type="checkbox" checked={viewMonthly} onChange={(e) => setViewMonthly(e.target.checked)} />
                <span>Monthly view</span>
              </label>
              {viewMonthly && (
                <div className="flex items-center space-x-2">
                  <select value={selectedMonth} onChange={(e) => setSelectedMonth(parseInt(e.target.value))} className="input">
                    {[...Array(12)].map((_, i) => (
                      <option key={i} value={i + 1}>{new Date(0, i).toLocaleString(undefined, { month: 'long' })}</option>
                    ))}
                  </select>
                  <input type="number" value={selectedYear} onChange={(e) => setSelectedYear(parseInt(e.target.value))} className="input w-28" />
                  <button className="btn btn-ghost" onClick={() => fetchSummary()}>Go</button>
                </div>
              )}
            </div>
          </div>
          {summary && <DashboardSummary summary={summary} />}

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {summary && <CategoryChart summary={summary} />}
            
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
              <ImportExport onImportSuccess={handleRefresh} />
            </div>
          </div>

          {/* Transaction Form */}
          <div className="mb-8">
            <TransactionForm onSuccess={handleRefresh} hasEntity={!!user?.entity_id} />
          </div>

          {/* Transaction List */}
          <TransactionList
            refreshTrigger={refreshTrigger}
            onUpdate={handleRefresh}
            onDelete={handleRefresh}
            showEntityInfo={!!user?.entity_id}
          />
        </div>
      </div>
    </>
  );
};
