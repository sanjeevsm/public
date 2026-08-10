import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
import { User } from '../types/user';

export const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const resp = await apiClient.get<User[]>('/api/admin/users');
        setUsers(resp.data);
      } catch (err) {
        console.error('Failed to load users', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Superadmin Dashboard</h1>
      <p className="mb-4">Overview and user management (read-only view).</p>
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
