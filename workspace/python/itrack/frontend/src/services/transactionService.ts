import { apiClient } from './api';
import {
  Transaction,
  TransactionInput,
  TransactionSummary,
  ImportResult,
  MonthlyDataPoint,
  RecurringTransaction,
} from '../types/transaction';

export const transactionService = {
  async getTransactions(params?: {
    skip?: number;
    limit?: number;
    type?: string;
    category?: string;
    currency?: string;
  }): Promise<Transaction[]> {
    const response = await apiClient.get<Transaction[]>('/api/transactions', { params });
    return response.data;
  },

  async getTransaction(id: string): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/api/transactions/${id}`);
    return response.data;
  },

  async createTransaction(data: TransactionInput): Promise<Transaction> {
    const response = await apiClient.post<Transaction>('/api/transactions', data);
    return response.data;
  },

  async updateTransaction(id: string, data: Partial<TransactionInput>): Promise<Transaction> {
    const response = await apiClient.put<Transaction>(`/api/transactions/${id}`, data);
    return response.data;
  },

  async deleteTransaction(id: string): Promise<void> {
    await apiClient.delete(`/api/transactions/${id}`);
  },

  async getSummary(currency?: string): Promise<TransactionSummary> {
    const response = await apiClient.get<TransactionSummary>('/api/transactions/summary', {
      params: currency ? { currency } : undefined,
    });
    return response.data;
  },
  async getMonthlySummary(year: number, month: number, currency?: string): Promise<TransactionSummary> {
    const response = await apiClient.get<TransactionSummary>('/api/transactions/summary', {
      params: { year, month, ...(currency && { currency }) },
    });
    return response.data;
  },

  async getMultiCurrencySummary(currencies: string[]): Promise<TransactionSummary[]> {
    const response = await apiClient.get<TransactionSummary[]>('/api/transactions/summary/multi-currency', {
      params: { currencies: currencies.join(',') },
    });
    return response.data;
  },

  async getConsolidatedSummary(currencies: string[]): Promise<{ currencies: TransactionSummary[]; note: string }> {
    const response = await apiClient.get('/api/transactions/summary/consolidated', {
      params: { currencies: currencies.join(',') },
    });
    return response.data;
  },

  async exportTransactions(): Promise<Blob> {
    const response = await apiClient.get('/api/transactions/export', {
      responseType: 'blob',
    });
    return response.data;
  },

  async importTransactions(file: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ImportResult>(
      '/api/transactions/import',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
  async bulkCreate(transactions: TransactionInput[]): Promise<{ inserted: number; failed: number; errors: any[] }> {
    const response = await apiClient.post('/api/transactions/bulk', transactions);
    return response.data;
  },

  async getMonthlyHistory(months = 6, currency?: string): Promise<MonthlyDataPoint[]> {
    const params: any = { months };
    if (currency) params.currency = currency;
    const response = await apiClient.get<MonthlyDataPoint[]>('/api/transactions/history', { params });
    return response.data;
  },

  async getRecurringTransactions(currency?: string): Promise<RecurringTransaction[]> {
    const params = currency ? { currency } : undefined;
    const response = await apiClient.get<RecurringTransaction[]>('/api/transactions/recurring', { params });
    return response.data;
  },
};
