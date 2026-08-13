import React, { useState } from 'react';
import { EntityCreate, EntityType } from '../types/entity';
import { entityService } from '../services/entityService';

interface EntityCreateFormProps {
  onSuccess: () => void;
  onCancel?: () => void;
}

export const EntityCreateForm: React.FC<EntityCreateFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<EntityCreate>({
    name: '',
    entity_type: 'Home',
    custom_type_name: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validation
      if (!formData.name.trim()) {
        setError('Entity name is required');
        setLoading(false);
        return;
      }

      if (formData.entity_type === 'Custom' && !formData.custom_type_name?.trim()) {
        setError('Custom type name is required for custom entities');
        setLoading(false);
        return;
      }

      const data: EntityCreate = {
        name: formData.name.trim(),
        entity_type: formData.entity_type,
        description: formData.description?.trim() || undefined
      };

      if (formData.entity_type === 'Custom') {
        data.custom_type_name = formData.custom_type_name?.trim();
      }

      await entityService.createEntity(data);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create entity');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Create Entity</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Entity Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entity Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Smith Family, Marketing Team"
              required
            />
          </div>

          {/* Entity Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entity Type *
            </label>
            <select
              value={formData.entity_type}
              onChange={(e) => setFormData({ ...formData, entity_type: e.target.value as EntityType })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Home">Home (Family/Household)</option>
              <option value="Office">Office (Workplace/Team)</option>
              <option value="Custom">Custom (Other)</option>
            </select>
          </div>

          {/* Custom Type Name (only if Custom selected) */}
          {formData.entity_type === 'Custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Custom Type Name *
              </label>
              <input
                type="text"
                value={formData.custom_type_name}
                onChange={(e) => setFormData({ ...formData, custom_type_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Club, Group, Association"
                required
              />
            </div>
          )}

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Brief description of this entity"
              rows={3}
            />
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> You will be the admin of this entity. You can invite other members later.
            </p>
          </div>

          {/* Buttons */}
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Creating...' : 'Create Entity'}
            </button>
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 disabled:bg-gray-200 disabled:cursor-not-allowed transition"
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};
