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

  // Get entity summary
  async getEntitySummary(entityId: string, includePrivate: boolean = false): Promise<EntitySummary> {
    const response = await api.get(`/api/entities/${entityId}/summary`, {
      params: { include_private: includePrivate }
    });
    return response.data;
  }
};
