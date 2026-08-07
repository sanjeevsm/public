import { apiClient } from './api';
import { User, UserRegister, UserLogin, AuthResponse } from '../types/user';

export const authService = {
  async register(userData: UserRegister): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/register', userData);
    return response.data;
  },

  async login(credentials: UserLogin): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);
    const { access_token } = response.data;
    
    // Store token
    localStorage.setItem('access_token', access_token);
    
    // Fetch and store user info
    const user = await this.getCurrentUser();
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
