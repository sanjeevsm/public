import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../services/api';
import { User } from '../types/user';
import { useConfirm } from '../components/ConfirmProvider';
import { useToast } from '../components/ToastProvider';
import { useAuth } from '../contexts/AuthContext';

export const AdminPage: React.FC = () => {
  const confirm = useConfirm();
  const { showToast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const { user: currentUser } = useAuth();

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

  const navigate = useNavigate();

  const promoteToAdmin = async (u: User) => {
    const ok = await confirm({ message: `Promote ${u.username} to entity admin?` });
    if (!ok) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { entity_role: 'admin' });
      await loadUsers();
      showToast('Promoted to admin', 'success');
    } catch (err) {
      console.error('Promote failed', err);
      showToast('Promote failed', 'error');
    } finally {
      setBusyId(null);
    }
  };

  const demoteFromAdmin = async (u: User) => {
    const ok = await confirm({ message: `Demote ${u.username} from entity admin?` });
    if (!ok) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { entity_role: null });
      await loadUsers();
      showToast('Demoted from admin', 'success');
    } catch (err) {
      console.error('Demote failed', err);
      showToast('Demote failed', 'error');
    } finally {
      setBusyId(null);
    }
  };

  const toggleSuperadmin = async (u: User) => {
    const to = !u.is_superadmin;
    if (u.is_superadmin === false) {
      const existingCount = users.filter(x => x.is_superadmin).length;
      if (existingCount > 0) {
        showToast('There is already a superadmin; only one is allowed.', 'warn');
        return;
      }
    }
    const ok = await confirm({ message: `${to ? 'Grant' : 'Revoke'} superadmin for ${u.username}?` });
    if (!ok) return;
    setBusyId(u.id);
    try {
      await apiClient.put(`/api/admin/users/${u.id}`, { is_superadmin: to });
      await loadUsers();
      showToast('Superadmin status changed', 'success');
    } catch (err) {
      console.error('Toggle superadmin failed', err);
      showToast('Toggle superadmin failed', 'error');
    } finally {
      setBusyId(null);
    }
  };

  const deleteUser = async (u: User) => {
    if (u.is_superadmin) {
      showToast('Cannot delete a superadmin account', 'warn');
      return;
    }
    const ok = await confirm({ message: `Delete user ${u.username}? This action is irreversible.` });
    if (!ok) return;
    setBusyId(u.id);
    try {
      await apiClient.delete(`/api/admin/users/${u.id}`);
      await loadUsers();
      showToast('User deleted', 'success');
    } catch (err) {
      console.error('Delete failed', err);
      showToast('Delete failed', 'error');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="p-6" style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Superadmin Dashboard</h1>
          <p className="text-sm text-gray-600">Overview and user management.</p>
        </div>
        <div>
          <button onClick={() => navigate(-1)} className="btn btn-secondary">Back</button>
        </div>
      </div>
      
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
                    {currentUser && currentUser.id === u.id ? (
                      <span className="text-sm muted">No actions for your account</span>
                    ) : (
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
                          disabled={busyId === u.id || (!u.is_superadmin && users.filter(x => x.is_superadmin).length > 0)}
                          onClick={() => toggleSuperadmin(u)}
                          className="px-2 py-1 bg-indigo-600 text-white rounded text-sm disabled:opacity-50"
                        >
                          {u.is_superadmin ? 'Revoke SA' : 'Grant SA'}
                        </button>

                        <button
                          disabled={busyId === u.id || u.is_superadmin}
                          onClick={() => deleteUser(u)}
                          className="px-2 py-1 bg-red-600 text-white rounded text-sm disabled:opacity-50"
                        >
                          Delete
                        </button>
                      </div>
                    )}
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
