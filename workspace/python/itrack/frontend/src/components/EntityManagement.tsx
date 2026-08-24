import React, { useState, useEffect } from 'react';
import { Entity, EntityMember, MemberRole } from '../types/entity';
import { entityService } from '../services/entityService';
import { useSettings } from '../contexts/SettingsContext';

interface EntityManagementProps {
  entity: Entity;
  currentUserId: string;
  isAdmin: boolean;
  onUpdate: () => void;
}

export const EntityManagement: React.FC<EntityManagementProps> = ({
  entity,
  currentUserId,
  isAdmin,
  onUpdate
}) => {
  const { formatDate } = useSettings();
  const [members, setMembers] = useState<EntityMember[]>([]);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<MemberRole>('member');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadMembers();
  }, [entity.id]);

  const loadMembers = async () => {
    try {
      const data = await entityService.getMembers(entity.id);
      setMembers(data);
    } catch (err: any) {
      console.error('Failed to load members:', err);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await entityService.inviteMember(entity.id, {
        user_email: inviteEmail,
        role: inviteRole
      });
      setSuccess('Member invited successfully!');
      setInviteEmail('');
      setShowInviteForm(false);
      loadMembers();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to invite member');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string, username: string) => {
    if (!window.confirm(`Are you sure you want to remove ${username} from the entity?`)) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      await entityService.removeMember(entity.id, memberId);
      setSuccess('Member removed successfully!');
      loadMembers();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handleChangeRole = async (memberId: string, username: string, currentRole: MemberRole) => {
    const newRole: MemberRole = currentRole === 'admin' ? 'member' : 'admin';
    const action = newRole === 'admin' ? 'promote' : 'demote';

    if (!window.confirm(`Are you sure you want to ${action} ${username} to ${newRole}?`)) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      await entityService.changeMemberRole(entity.id, memberId, newRole);
      setSuccess(`Member role updated successfully!`);
      loadMembers();
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change member role');
    }
  };

  const handleDeleteEntity = async () => {
    const confirmed = window.confirm(
      `Delete "${entity.name}"?\n\nThis will permanently remove the entity and disconnect all members. Transactions will not be deleted but will become private.\n\nType the entity name to confirm.`
    );
    if (!confirmed) return;

    const typedName = window.prompt(`Type "${entity.name}" to confirm deletion:`);
    if (typedName !== entity.name) {
      setError('Entity name did not match. Deletion cancelled.');
      return;
    }

    setError('');
    setLoading(true);
    try {
      await entityService.deleteEntity(entity.id);
      setSuccess('Entity deleted successfully.');
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete entity');
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveEntity = async () => {
    if (!window.confirm('Are you sure you want to leave this entity? You will lose access to all entity data.')) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      await entityService.leaveEntity();
      setSuccess('Left entity successfully!');
      onUpdate();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to leave entity');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Entity Management</h2>
        {isAdmin && (
          <button
            onClick={() => setShowInviteForm(!showInviteForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
          >
            {showInviteForm ? 'Cancel' : '+ Invite Member'}
          </button>
        )}
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md">
          {success}
        </div>
      )}

      {/* Invite Form */}
      {isAdmin && showInviteForm && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Invite New Member</h3>
          <form onSubmit={handleInvite} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="member@example.com"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                User must already have an iTrack+ account
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as MemberRole)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="member">Member (View shared transactions)</option>
                <option value="admin">Admin (Full access)</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Inviting...' : 'Send Invitation'}
            </button>
          </form>
        </div>
      )}

      {/* Entity Info */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">{entity.name}</h3>
        <div className="space-y-1 text-sm text-gray-600">
          <p><strong>Type:</strong> {entity.entity_type} {entity.custom_type_name && `(${entity.custom_type_name})`}</p>
          {entity.description && <p><strong>Description:</strong> {entity.description}</p>}
          <p><strong>Created:</strong> {formatDate(entity.created_at)}</p>
          <p><strong>Total Members:</strong> {members.length}</p>
        </div>
      </div>

      {/* Members List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Members</h3>
        <div className="space-y-2">
          {members.map((member) => {
            const isCurrentUser = member.user_id === currentUserId;
            const isCreator = member.user_id === entity.created_by;

            return (
              <div
                key={member.user_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    {member.username.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">
                      {member.username}
                      {isCurrentUser && <span className="ml-2 text-xs text-blue-600">(You)</span>}
                      {isCreator && <span className="ml-2 text-xs text-purple-600">(Creator)</span>}
                    </p>
                    <p className="text-sm text-gray-500">
                      Joined {formatDate(member.joined_at)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    member.role === 'admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {member.role === 'admin' ? '👑 Admin' : '👤 Member'}
                  </span>

                  {isAdmin && !isCurrentUser && (
                    <div className="flex space-x-1">
                      <button
                        onClick={() => handleChangeRole(member.user_id, member.username, member.role)}
                        className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
                        title={member.role === 'admin' ? 'Demote to Member' : 'Promote to Admin'}
                      >
                        {member.role === 'admin' ? '⬇️ Demote' : '⬆️ Promote'}
                      </button>
                      <button
                        onClick={() => handleRemoveMember(member.user_id, member.username)}
                        className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
                        title="Remove Member"
                      >
                        🗑️ Remove
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Leave / Delete Entity */}
      <div className="mt-6 pt-6 border-t border-gray-200 space-y-3">
        <button
          onClick={handleLeaveEntity}
          className="w-full bg-red-100 text-red-700 py-2 px-4 rounded-md hover:bg-red-200 transition font-medium"
        >
          Leave Entity
        </button>
        <p className="text-xs text-gray-500 text-center">
          {isAdmin && members.filter(m => m.role === 'admin').length === 1
            ? '⚠️ You are the only admin. Promote another member before leaving.'
            : 'You can rejoin if invited again.'}
        </p>

        {isAdmin && (
          <>
            <div className="border-t border-gray-200 pt-3">
              <button
                onClick={handleDeleteEntity}
                disabled={loading}
                className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium"
              >
                🗑️ Delete Entity
              </button>
              <p className="mt-1 text-xs text-gray-500 text-center">
                Permanently deletes the entity and disconnects all members.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
