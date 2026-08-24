import React, { useState, useEffect } from 'react';
import { Users, UserPlus, UserX, Shield, User, Mail, Calendar } from 'lucide-react';
import { Entity, EntityMember } from '../types/entity';
import { entityService } from '../services/entityService';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

export const MemberManagement: React.FC = () => {
  const { user } = useAuth();
  const { formatDate } = useSettings();
  const [entity, setEntity] = useState<Entity | null>(null);
  const [members, setMembers] = useState<EntityMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [isInviting, setIsInviting] = useState(false);

  useEffect(() => {
    loadEntity();
  }, []);

  const loadEntity = async () => {
    try {
      setLoading(true);
      const entityData = await entityService.getMyEntity();
      setEntity(entityData);
      const memberData = await entityService.getMembers(entityData.id);
      setMembers(memberData);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('You are not part of any entity. Create or join one first.');
      } else {
        setError('Failed to load entity information');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsInviting(true);

    if (!entity) return;
    try {
      await entityService.inviteMember(entity.id, { user_email: inviteEmail, role: 'member' });
      setSuccess(`Invitation sent to ${inviteEmail}`);
      setInviteEmail('');
      loadEntity();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setIsInviting(false);
    }
  };

  const handleRemoveMember = async (memberId: string, memberName: string) => {
    if (!window.confirm(`Are you sure you want to remove ${memberName} from the entity?`)) {
      return;
    }
    if (!entity) return;

    try {
      await entityService.removeMember(entity.id, memberId);
      setSuccess(`${memberName} removed successfully`);
      loadEntity();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handlePromoteMember = async (memberId: string, memberName: string) => {
    if (!window.confirm(`Promote ${memberName} to admin? They will have full control over the entity.`)) {
      return;
    }
    if (!entity) return;

    try {
      await entityService.changeMemberRole(entity.id, memberId, 'admin');
      setSuccess(`${memberName} promoted to admin`);
      loadEntity();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to promote member');
    }
  };

  const handleDemoteMember = async (memberId: string, memberName: string) => {
    if (!window.confirm(`Demote ${memberName} to member? They will have limited permissions.`)) {
      return;
    }
    if (!entity) return;

    try {
      await entityService.changeMemberRole(entity.id, memberId, 'member');
      setSuccess(`${memberName} demoted to member`);
      loadEntity();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to demote member');
    }
  };

  const isAdmin = members.find(m => m.user_id === user?.id)?.role === 'admin';
  const isOwner = entity?.created_by === user?.id;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <Users className="text-blue-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Member Management</h1>
            <p className="text-gray-600">Manage entity members and permissions</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-700">
          {success}
        </div>
      )}

      {loading ? (
        <div className="card">
          <p className="text-gray-600">Loading entity information...</p>
        </div>
      ) : !entity ? (
        <div className="card">
          <p className="text-gray-600">You are not part of any entity.</p>
        </div>
      ) : (
        <>
          {/* Entity Info */}
          <div className="card bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold">{entity.name}</h2>
                <p className="text-blue-100 mt-1">{entity.entity_type}</p>
                <p className="text-blue-100 text-sm mt-2">{entity.description}</p>
              </div>
              <div className="text-right">
                <p className="text-blue-100 text-sm">Total Members</p>
                <p className="text-4xl font-bold">{members.length}</p>
              </div>
            </div>
          </div>

          {/* Invite Form (Admin Only) */}
          {isAdmin && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4 flex items-center space-x-2">
                <UserPlus size={24} className="text-blue-600" />
                <span>Invite New Member</span>
              </h2>
              <form onSubmit={handleInvite} className="flex space-x-3">
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="input flex-1"
                  disabled={isInviting}
                />
                <button
                  type="submit"
                  disabled={isInviting}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <UserPlus size={18} />
                  <span>{isInviting ? 'Sending...' : 'Send Invite'}</span>
                </button>
              </form>
              <p className="text-sm text-gray-600 mt-2">
                The user must have an account to receive the invitation.
              </p>
            </div>
          )}

          {/* Members List */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">
              Entity Members ({members.length})
            </h2>
            <div className="space-y-3">
              {members.map((member) => {
                const isCurrentUser = member.user_id === user?.id;
                const canModify = isAdmin && !isCurrentUser && (isOwner || member.role !== 'admin');

                return (
                  <div
                    key={member.user_id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        member.role === 'admin' ? 'bg-purple-100' : 'bg-blue-100'
                      }`}>
                        {member.role === 'admin' ? (
                          <Shield className="text-purple-600" size={24} />
                        ) : (
                          <User className="text-blue-600" size={24} />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-800">
                            {member.username}
                          </h3>
                          {isCurrentUser && (
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                              You
                            </span>
                          )}
                          {entity.created_by === member.user_id && (
                            <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded">
                              Owner
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-3 mt-1">
                          <p className="text-sm text-gray-600 flex items-center space-x-1">
                            <Mail size={14} />
                            <span>{member.email}</span>
                          </p>
                          <span className={`px-2 py-0.5 text-xs rounded ${
                            member.role === 'admin'
                              ? 'bg-purple-100 text-purple-700'
                              : 'bg-gray-200 text-gray-700'
                          }`}>
                            {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 flex items-center space-x-1">
                          <Calendar size={12} />
                          <span>Joined {formatDate(member.joined_at)}</span>
                        </p>
                      </div>
                    </div>

                    {/* Actions (Admin Only) */}
                    {canModify && (
                      <div className="flex space-x-2">
                        {member.role === 'member' ? (
                          <button
                            onClick={() => handlePromoteMember(member.user_id, member.username)}
                            className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition flex items-center space-x-1"
                            title="Promote to Admin"
                          >
                            <Shield size={16} />
                            <span className="text-sm">Promote</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleDemoteMember(member.user_id, member.username)}
                            className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition flex items-center space-x-1"
                            title="Demote to Member"
                          >
                            <User size={16} />
                            <span className="text-sm">Demote</span>
                          </button>
                        )}
                        <button
                          onClick={() => handleRemoveMember(member.user_id, member.username)}
                          className="px-3 py-1.5 bg-red-100 text-red-700 rounded hover:bg-red-200 transition flex items-center space-x-1"
                          title="Remove Member"
                        >
                          <UserX size={16} />
                          <span className="text-sm">Remove</span>
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Permissions Info */}
          <div className="card bg-blue-50 border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2 flex items-center space-x-2">
              <Shield size={20} />
              <span>Permission Levels</span>
            </h3>
            <div className="space-y-2 text-sm text-blue-800">
              <p><strong>Admin:</strong> Full control - manage members, view all transactions, edit entity settings</p>
              <p><strong>Member:</strong> Limited access - add personal transactions, view shared transactions</p>
              <p><strong>Owner:</strong> Special admin with full ownership rights (cannot be removed)</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
