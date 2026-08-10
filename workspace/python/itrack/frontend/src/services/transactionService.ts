import { apiClient } from './api';
import {
  Transaction,
  TransactionInput,
  TransactionSummary,
  ImportResult,
} from '../types/transaction';

export const transactionService = {
  async getTransactions(params?: {
    skip?: number;
    limit?: number;
    type?: string;
    category?: string;
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

  async getSummary(): Promise<TransactionSummary> {
    const response = await apiClient.get<TransactionSummary>('/api/transactions/summary');
    return response.data;
  },
  async getMonthlySummary(year: number, month: number): Promise<TransactionSummary> {
    const response = await apiClient.get<TransactionSummary>('/api/transactions/summary', { params: { year, month } });
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
};
