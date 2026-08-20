import React, { useState, useEffect } from 'react';
import { Tag, Plus, Edit2, Trash2, TrendingUp, TrendingDown, Wallet, PieChart } from 'lucide-react';
import { Category, CategoryCreate, CategoryUpdate, CategoryType } from '../types/category';
import { categoryService } from '../services/categoryService';

export const CategoryManagement: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [filterType, setFilterType] = useState<CategoryType | 'all'>('all');

  const [formData, setFormData] = useState<CategoryCreate>({
    name: '',
    type: 'expense',
    color: '#3B82F6',
    icon: '📌',
    description: '',
    is_default: false,
  });

  const iconOptions = ['💰', '💼', '📈', '🏢', '🍔', '🚗', '🛍️', '🎬', '💡', '⚕️', '📚', '🏠', '📌', '🎯', '💳', '💵', '📊', '🏡', '💎', '🏦', '💸'];
  const colorOptions = [
    '#EF4444', '#F97316', '#F59E0B', '#10B981', '#059669', '#14B8A6',
    '#3B82F6', '#6366F1', '#8B5CF6', '#EC4899', '#F43F5E', '#6B7280',
  ];

  useEffect(() => {
    loadCategories();
  }, [filterType]);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const type = filterType === 'all' ? undefined : filterType;
      const data = await categoryService.getCategories(type);
      setCategories(data);
    } catch (err: any) {
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingCategory) {
        const updateData: CategoryUpdate = {
          name: formData.name,
          type: formData.type,
          color: formData.color,
          icon: formData.icon,
          description: formData.description,
        };
        await categoryService.updateCategory(editingCategory.id, updateData);
        setSuccess('Category updated successfully');
      } else {
        await categoryService.createCategory(formData);
        setSuccess('Category created successfully');
      }

      resetForm();
      loadCategories();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    }
  };

  const handleEdit = (category: Category) => {
    if (category.is_default) {
      setError('Cannot edit default categories');
      return;
    }
    setEditingCategory(category);
    setFormData({
      name: category.name,
      type: category.type,
      color: category.color || '#3B82F6',
      icon: category.icon || '📌',
      description: category.description || '',
      is_default: false,
    });
    setShowForm(true);
  };

  const handleDelete = async (categoryId: string, isDefault: boolean) => {
    if (isDefault) {
      setError('Cannot delete default categories');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this category?')) {
      return;
    }

    try {
      await categoryService.deleteCategory(categoryId);
      setSuccess('Category deleted successfully');
      loadCategories();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete category');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'expense',
      color: '#3B82F6',
      icon: '📌',
      description: '',
      is_default: false,
    });
    setEditingCategory(null);
    setShowForm(false);
  };

  const filteredCategories = categories.filter(cat => {
    if (filterType === 'all') return true;
    return cat.type === filterType || cat.type === 'both';
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <Tag className="text-purple-600" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Category Management</h1>
            <p className="text-gray-600">Organize your transactions with custom categories</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>{showForm ? 'Cancel' : 'Add Category'}</span>
        </button>
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

      {/* Form */}
      {showForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">
            {editingCategory ? 'Edit Category' : 'Create New Category'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                  placeholder="e.g., Groceries"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type *
                </label>
                <select
                  required
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as CategoryType })}
                  className="input"
                >
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                  <option value="asset">Asset</option>
                  <option value="liability">Liability</option>
                  <option value="both">Both</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Icon
                </label>
                <div className="grid grid-cols-8 gap-2">
                  {iconOptions.map((icon) => (
                    <button
                      key={icon}
                      type="button"
                      onClick={() => setFormData({ ...formData, icon })}
                      className={`p-2 text-2xl border rounded-md hover:bg-gray-100 transition ${
                        formData.icon === icon ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                      }`}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Color
                </label>
                <div className="grid grid-cols-6 gap-2">
                  {colorOptions.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setFormData({ ...formData, color })}
                      className={`w-10 h-10 rounded-md border-2 transition ${
                        formData.color === color ? 'border-gray-800 scale-110' : 'border-gray-300'
                      }`}
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input"
                rows={2}
                placeholder="Optional description"
              />
            </div>

            <div className="flex space-x-3">
              <button type="submit" className="btn btn-primary flex-1">
                {editingCategory ? 'Update Category' : 'Create Category'}
              </button>
              <button type="button" onClick={resetForm} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filter */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Filter:</label>
          <div className="flex space-x-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 rounded-md transition ${
                filterType === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('income')}
              className={`px-4 py-2 rounded-md transition flex items-center space-x-2 ${
                filterType === 'income'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <TrendingUp size={16} />
              <span>Income</span>
            </button>
            <button
              onClick={() => setFilterType('expense')}
              className={`px-4 py-2 rounded-md transition flex items-center space-x-2 ${
                filterType === 'expense'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <TrendingDown size={16} />
              <span>Expense</span>
            </button>
            <button
              onClick={() => setFilterType('asset')}
              className={`px-4 py-2 rounded-md transition flex items-center space-x-2 ${
                filterType === 'asset'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <Wallet size={16} />
              <span>Asset</span>
            </button>
            <button
              onClick={() => setFilterType('liability')}
              className={`px-4 py-2 rounded-md transition flex items-center space-x-2 ${
                filterType === 'liability'
                  ? 'bg-orange-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <PieChart size={16} />
              <span>Liability</span>
            </button>
          </div>
        </div>
      </div>

      {/* Category Grid */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">
          Categories ({filteredCategories.length})
        </h2>
        {loading ? (
          <p className="text-gray-600">Loading categories...</p>
        ) : filteredCategories.length === 0 ? (
          <p className="text-gray-600">No categories found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCategories.map((category) => (
              <div
                key={category.id}
                className="p-4 border-2 rounded-lg hover:shadow-md transition"
                style={{ borderColor: category.color || '#3B82F6' }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{category.icon}</span>
                    <div>
                      <h3 className="font-semibold text-gray-800">{category.name}</h3>
                      <p className="text-xs text-gray-500">
                        {category.type === 'income' && <TrendingUp size={12} className="inline mr-1" />}
                        {category.type === 'expense' && <TrendingDown size={12} className="inline mr-1" />}
                        {category.type === 'asset' && <Wallet size={12} className="inline mr-1" />}
                        {category.type === 'liability' && <PieChart size={12} className="inline mr-1" />}
                        {category.type.charAt(0).toUpperCase() + category.type.slice(1)}
                      </p>
                    </div>
                  </div>
                  {category.is_default ? (
                    <span className="px-2 py-1 bg-gray-200 text-gray-600 text-xs rounded">
                      Default
                    </span>
                  ) : (
                    <div className="flex space-x-1">
                      <button
                        onClick={() => handleEdit(category)}
                        className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        title="Edit"
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        onClick={() => handleDelete(category.id, category.is_default)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                </div>
                {category.description && (
                  <p className="text-sm text-gray-600 mt-2">{category.description}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
