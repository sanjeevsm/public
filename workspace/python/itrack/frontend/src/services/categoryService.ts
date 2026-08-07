import api from './api';
import { Category, CategoryCreate, CategoryUpdate, CategoryStats } from '../types/category';

export const categoryService = {
  /**
   * Initialize default categories
   */
  initializeDefaults: async (): Promise<{ message: string }> => {
    const response = await api.post('/categories/initialize');
    return response.data;
  },

  /**
   * Create a new custom category
   */
  createCategory: async (data: CategoryCreate): Promise<Category> => {
    const response = await api.post('/categories', data);
    return response.data;
  },

  /**
   * Get all categories (default + custom)
   */
  getCategories: async (type?: 'income' | 'expense'): Promise<Category[]> => {
    const params = type ? { type } : {};
    const response = await api.get('/categories', { params });
    return response.data;
  },

  /**
   * Get category usage statistics
   */
  getCategoryStats: async (): Promise<CategoryStats> => {
    const response = await api.get('/categories/stats');
    return response.data;
  },

  /**
   * Get a specific category
   */
  getCategory: async (categoryId: string): Promise<Category> => {
    const response = await api.get(`/categories/${categoryId}`);
    return response.data;
  },

  /**
   * Update a custom category
   */
  updateCategory: async (
    categoryId: string,
    data: CategoryUpdate
  ): Promise<Category> => {
    const response = await api.put(`/categories/${categoryId}`, data);
    return response.data;
  },

  /**
   * Delete a custom category
   */
  deleteCategory: async (categoryId: string): Promise<void> => {
    await api.delete(`/categories/${categoryId}`);
  },
};
