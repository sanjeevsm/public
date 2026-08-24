import api from './api';
import {
  Entity,
  EntityCreate,
  EntityUpdate,
  EntityInvite,
  EntitySummary,
  EntityMember,
  MemberRole
} from '../types/entity';
import { MonthlyDataPoint, RecurringTransaction } from '../types/transaction';

export const entityService = {
  // Create a new entity
  async createEntity(data: EntityCreate): Promise<Entity> {
    const response = await api.post('/api/entities', data);
    return response.data;
  },

  // Get user's entity
  async getMyEntity(): Promise<Entity> {
    const response = await api.get('/api/entities/my-entity');
    return response.data;
  },

  // Get entity by ID
  async getEntity(entityId: string): Promise<Entity> {
    const response = await api.get(`/api/entities/${entityId}`);
    return response.data;
  },

  // Update entity (admin only)
  async updateEntity(entityId: string, data: EntityUpdate): Promise<Entity> {
    const response = await api.put(`/api/entities/${entityId}`, data);
    return response.data;
  },

  // Invite member (admin only)
  async inviteMember(entityId: string, data: EntityInvite): Promise<{ message: string }> {
    const response = await api.post(`/api/entities/${entityId}/invite`, data);
    return response.data;
  },

  // Leave entity
  async leaveEntity(): Promise<{ message: string }> {
    const response = await api.post('/api/entities/leave');
    return response.data;
  },

  // Remove member (admin only)
  async removeMember(entityId: string, memberId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/entities/${entityId}/members/${memberId}`);
    return response.data;
  },

  // Change member role (admin only)
  async changeMemberRole(
    entityId: string,
    memberId: string,
    role: MemberRole
  ): Promise<{ message: string }> {
    const response = await api.put(`/api/entities/${entityId}/members/${memberId}/role`, { role });
    return response.data;
  },

  // Get entity members
  async getMembers(entityId: string): Promise<EntityMember[]> {
    const response = await api.get(`/api/entities/${entityId}/members`);
    return response.data;
  },

  // Get entity summary (optionally scoped to a specific month)
  async getEntitySummary(
    entityId: string,
    includePrivate: boolean = false,
    month?: number,
    year?: number,
    currency?: string,
  ): Promise<EntitySummary> {
    const response = await api.get(`/api/entities/${entityId}/summary`, {
      params: { include_private: includePrivate, month, year, currency },
    });
    return response.data;
  },

  // Delete entity (admin only)
  async deleteEntity(entityId: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/entities/${entityId}`);
    return response.data;
  },

  // Monthly history for forecast
  async getEntityHistory(entityId: string, months = 6, includePrivate = false, currency?: string): Promise<MonthlyDataPoint[]> {
    const response = await api.get<MonthlyDataPoint[]>(`/api/entities/${entityId}/history`, {
      params: { months, include_private: includePrivate, currency },
    });
    return response.data;
  },

  async getEntityTransactions(
    entityId: string,
    includePrivate = false,
    currency?: string,
    skip = 0,
    limit = 50,
  ): Promise<any[]> {
    const response = await api.get(`/api/entities/${entityId}/transactions`, {
      params: { include_private: includePrivate, currency, skip, limit },
    });
    return response.data;
  },

  async getEntityRecurringTransactions(entityId: string, includePrivate = false, currency?: string): Promise<RecurringTransaction[]> {
    const response = await api.get<RecurringTransaction[]>(`/api/entities/${entityId}/recurring-transactions`, {
      params: { include_private: includePrivate, currency },
    });
    return response.data;
  },
};
