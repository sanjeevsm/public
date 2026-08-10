import { apiClient } from './api';
import { User, AdminUserUpdate } from '../types/user';

export const userService = {
  async getEntityMembersProfiles(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/api/users/entity-members');
    return response.data;
  },

  async adminUpdateUser(userId: string, data: AdminUserUpdate): Promise<User> {
    const response = await apiClient.put<User>(`/api/users/${userId}`, data);
    return response.data;
  },
};
