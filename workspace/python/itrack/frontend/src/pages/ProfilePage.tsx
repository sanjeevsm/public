import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';
import { authService } from '../services/authService';
import { userService } from '../services/userService';
import { User, AdminUserUpdate } from '../types/user';

export const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const { formatDate } = useSettings();
  const isAdmin = user?.entity_role === 'admin';

  // ── My Profile state ────────────────────────────────────────────
  const [username, setUsername] = useState(user?.username ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState('');
  const [profileSuccess, setProfileSuccess] = useState('');

  // ── Entity Members state (admin only) ───────────────────────────
  const [members, setMembers] = useState<User[]>([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [editingMember, setEditingMember] = useState<User | null>(null);
  const [editUsername, setEditUsername] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editError, setEditError] = useState('');
  const [editSuccess, setEditSuccess] = useState('');
  const [editLoading, setEditLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setUsername(user.username);
      setEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    if (isAdmin) loadMembers();
  }, [isAdmin]);

  const loadMembers = async () => {
    setMembersLoading(true);
    try {
      const data = await userService.getEntityMembersProfiles();
      setMembers(data);
    } catch {
      // non-critical
    } finally {
      setMembersLoading(false);
    }
  };

  // ── Own profile save ─────────────────────────────────────────────
  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError('');
    setProfileSuccess('');

    if (newPassword && newPassword !== confirmPassword) {
      setProfileError('New passwords do not match.');
      return;
    }

    setProfileLoading(true);
    try {
      await authService.updateProfile({
        username: username !== user?.username ? username : undefined,
        email: email !== user?.email ? email : undefined,
        current_password: currentPassword || undefined,
        new_password: newPassword || undefined,
      });
      await refreshUser();
      setProfileSuccess('Profile updated successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setProfileError(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setProfileLoading(false);
    }
  };

  // ── Admin edit member ────────────────────────────────────────────
  const openEditMember = (member: User) => {
    setEditingMember(member);
    setEditUsername(member.username);
    setEditEmail(member.email);
    setEditError('');
    setEditSuccess('');
  };

  const handleMemberSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingMember) return;
    setEditError('');
    setEditLoading(true);

    const patch: AdminUserUpdate = {};
    if (editUsername !== editingMember.username) patch.username = editUsername;
    if (editEmail !== editingMember.email) patch.email = editEmail;

    try {
      const updated = await userService.adminUpdateUser(editingMember.id, patch);
      setMembers(prev => prev.map(m => (m.id === updated.id ? updated : m)));
      setEditSuccess(`${updated.username}'s profile updated.`);
      setEditingMember(updated);
    } catch (err: any) {
      setEditError(err.response?.data?.detail || 'Failed to update member.');
    } finally {
      setEditLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">

        {/* ── My Profile ── */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {user?.username.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{user?.username}</h1>
              <p className="text-gray-500 text-sm">{user?.email}</p>
              {user?.entity_role && (
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                  {user.entity_role === 'admin' ? '👑 Admin' : '👤 Member'}
                </span>
              )}
            </div>
          </div>

          <h2 className="text-lg font-semibold text-gray-700 mb-4">Edit My Profile</h2>

          {profileError && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">{profileError}</div>}
          {profileSuccess && <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md text-sm">{profileSuccess}</div>}

          <form onSubmit={handleProfileSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  minLength={3} maxLength={50}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="border-t pt-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Change Password <span className="font-normal text-gray-400">(leave blank to keep current)</span></p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Current Password</label>
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={e => setCurrentPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Required to change password"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">New Password</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    minLength={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Min 8 characters"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Confirm New Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Repeat new password"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={profileLoading}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition font-medium"
              >
                {profileLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>

        {/* ── Entity Member Profiles (admin only) ── */}
        {isAdmin && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              Entity Member Profiles
              <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Admin</span>
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              As an admin you can update the username and email of members in your entity. You cannot change their passwords.
            </p>

            {membersLoading ? (
              <p className="text-gray-500 text-sm">Loading members...</p>
            ) : (
              <div className="space-y-3">
                {members.map(member => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-indigo-400 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {member.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">
                          {member.username}
                          {member.id === user?.id && <span className="ml-2 text-xs text-blue-600">(You)</span>}
                        </p>
                        <p className="text-xs text-gray-500">{member.email}</p>
                        <p className="text-xs text-gray-400">
                          {member.entity_role === 'admin' ? '👑 Admin' : '👤 Member'} · Joined {formatDate(member.created_at)}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => openEditMember(member)}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
                    >
                      Edit
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Inline edit panel */}
            {editingMember && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-3">
                  Editing: <span className="text-blue-700">{editingMember.username}</span>
                </h3>

                {editError && <div className="mb-3 p-2 bg-red-100 text-red-700 rounded text-sm">{editError}</div>}
                {editSuccess && <div className="mb-3 p-2 bg-green-100 text-green-700 rounded text-sm">{editSuccess}</div>}

                <form onSubmit={handleMemberSave} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                      <input
                        type="text"
                        value={editUsername}
                        onChange={e => setEditUsername(e.target.value)}
                        minLength={3} maxLength={50}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input
                        type="email"
                        value={editEmail}
                        onChange={e => setEditEmail(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={() => { setEditingMember(null); setEditError(''); setEditSuccess(''); }}
                      className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={editLoading}
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition"
                    >
                      {editLoading ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};
