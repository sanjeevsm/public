import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, ChevronRight } from 'lucide-react';
import { Entity } from '../types/entity';
import { entityService } from '../services/entityService';

interface EntityStatusBannerProps {
  hasEntity: boolean;
}

export const EntityStatusBanner: React.FC<EntityStatusBannerProps> = ({ hasEntity }) => {
  const [entity, setEntity] = useState<Entity | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (hasEntity) {
      loadEntity();
    }
  }, [hasEntity]);

  const loadEntity = async () => {
    setLoading(true);
    try {
      const entityData = await entityService.getMyEntity();
      setEntity(entityData);
    } catch (error) {
      console.error('Failed to load entity:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!hasEntity || loading) {
    return null;
  }

  // No entity banner
  if (!entity) {
    return (
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg shadow-lg p-6 mb-6 relative">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <Users size={24} />
            </div>
          </div>
          
          <div className="flex-1">
            <h3 className="text-xl font-bold mb-2">
              🏠 Create Your Entity
            </h3>
            <p className="text-blue-100 mb-4">
              Start tracking finances with your family, team, or any group! 
              Create an entity to collaborate while maintaining your privacy.
            </p>
            <Link
              to="/entity"
              className="inline-flex items-center px-4 py-2 bg-white text-blue-600 rounded-md hover:bg-blue-50 transition font-semibold"
            >
              Get Started
              <ChevronRight size={18} className="ml-1" />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Has entity banner
  return (
    <div className="bg-gradient-to-r from-green-500 to-teal-600 text-white rounded-lg shadow-lg p-6 mb-6 relative">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
            <Users size={24} />
          </div>
        </div>
        
        <div className="flex-1">
          <h3 className="text-xl font-bold mb-2">
            {entity.entity_type === 'Home' ? '🏠' : entity.entity_type === 'Office' ? '💼' : '🎨'} {entity.name}
          </h3>
          <p className="text-green-100 mb-4">
            You're part of <strong>{entity.name}</strong> with {entity.members.length} {entity.members.length === 1 ? 'member' : 'members'}. 
            Manage your shared finances and view entity reports.
          </p>
          <div className="flex space-x-3">
            <Link
              to="/entity"
              className="inline-flex items-center px-4 py-2 bg-white text-green-600 rounded-md hover:bg-green-50 transition font-semibold"
            >
              View Entity Dashboard
              <ChevronRight size={18} className="ml-1" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
