import api from './api';
import { Budget, BudgetCreate, BudgetUpdate, BudgetProgress } from '../types/budget';

export const budgetService = {
  /**
   * Create a new budget
   */
  createBudget: async (data: BudgetCreate): Promise<Budget> => {
    const response = await api.post('/api/budgets', data);
    return response.data;
  },

  /**
   * Get all budgets
   */
  getBudgets: async (activeOnly: boolean = false): Promise<Budget[]> => {
    const params = activeOnly ? { active_only: true } : {};
    const response = await api.get('/api/budgets', { params });
    return response.data;
  },

  /**
   * Get progress for all active budgets
   */
  getBudgetsProgress: async (): Promise<BudgetProgress[]> => {
    const response = await api.get('/api/budgets/progress');
    return response.data;
  },

  /**
   * Get budget alerts (exceeded threshold)
   */
  getBudgetAlerts: async (): Promise<BudgetProgress[]> => {
    const response = await api.get('/api/budgets/alerts');
    return response.data;
  },

  /**
   * Get a specific budget
   */
  getBudget: async (budgetId: string): Promise<Budget> => {
    const response = await api.get(`/api/budgets/${budgetId}`);
    return response.data;
  },

  /**
   * Get progress for a specific budget
   */
  getBudgetProgress: async (budgetId: string): Promise<BudgetProgress> => {
    const response = await api.get(`/api/budgets/${budgetId}/progress`);
    return response.data;
  },

  /**
   * Update a budget
   */
  updateBudget: async (
    budgetId: string,
    data: BudgetUpdate
  ): Promise<Budget> => {
    const response = await api.put(`/api/budgets/${budgetId}`, data);
    return response.data;
  },

  /**
   * Delete a budget
   */
  deleteBudget: async (budgetId: string): Promise<void> => {
    await api.delete(`/api/budgets/${budgetId}`);
  },
};
