import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
import { User } from '../types/user';

export const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const resp = await apiClient.get<User[]>('/api/admin/users');
      setUsers(resp.data);
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const promoteToAdmin = async (u: User) => {
    if (!window.confirm(`Promote ${u.username} to entity admin?`)) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { entity_role: 'admin' });
      await loadUsers();
    } catch (err) {
      console.error('Promote failed', err);
      alert('Promote failed');
    } finally {
      setBusyId(null);
    }
  };

  const demoteFromAdmin = async (u: User) => {
    if (!window.confirm(`Demote ${u.username} from entity admin?`)) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { entity_role: null });
      await loadUsers();
    } catch (err) {
      console.error('Demote failed', err);
      alert('Demote failed');
    } finally {
      setBusyId(null);
    }
  };

  const toggleSuperadmin = async (u: User) => {
    const to = !u.is_superadmin;
    if (!window.confirm(`${to ? 'Grant' : 'Revoke'} superadmin for ${u.username}?`)) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { is_superadmin: to });
      await loadUsers();
    } catch (err) {
      console.error('Toggle superadmin failed', err);
      alert('Toggle superadmin failed');
    } finally {
      setBusyId(null);
    }
  };

  const deleteUser = async (u: User) => {
    if (!window.confirm(`Delete user ${u.username}? This action is irreversible.`)) return;
    setBusyId(u.id);
    try {
      await apiClient.delete(`/api/admin/users/${u.id}`);
      await loadUsers();
    } catch (err) {
      console.error('Delete failed', err);
      alert('Delete failed');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Superadmin Dashboard</h1>
      <p className="mb-4">Overview and user management.</p>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="bg-white rounded shadow overflow-hidden">
          <table className="min-w-full text-left">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2">Username</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Entity</th>
                <th className="px-4 py-2">Role</th>
                <th className="px-4 py-2">Superadmin</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-t">
                  <td className="px-4 py-2">{u.username}</td>
                  <td className="px-4 py-2">{u.email}</td>
                  <td className="px-4 py-2">{u.entity_id ?? '-'}</td>
                  <td className="px-4 py-2">{u.entity_role ?? '-'}</td>
                  <td className="px-4 py-2">{u.is_superadmin ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-2">
                    <div className="flex items-center gap-2">
                      {u.entity_role !== 'admin' ? (
                        <button
                          disabled={busyId === u.id}
                          onClick={() => promoteToAdmin(u)}
                          className="px-2 py-1 bg-green-600 text-white rounded text-sm"
                        >
                          Promote
                        </button>
                      ) : (
                        <button
                          disabled={busyId === u.id}
                          onClick={() => demoteFromAdmin(u)}
                          className="px-2 py-1 bg-yellow-600 text-white rounded text-sm"
                        >
                          Demote
                        </button>
                      )}

                      <button
                        disabled={busyId === u.id}
                        onClick={() => toggleSuperadmin(u)}
                        className="px-2 py-1 bg-indigo-600 text-white rounded text-sm"
                      >
                        {u.is_superadmin ? 'Revoke SA' : 'Grant SA'}
                      </button>

                      <button
                        disabled={busyId === u.id}
                        onClick={() => deleteUser(u)}
                        className="px-2 py-1 bg-red-600 text-white rounded text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminPage;
