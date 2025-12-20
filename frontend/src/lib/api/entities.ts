// Entity API service
import apiClient from './client';
import type { Entity, EntityListItem, EntitySearchParams } from '../types/entity';
import type { RelationshipResponse, GraphData } from '../types';

export const entitiesApi = {
  // Get a specific entity by ID
  getEntity: async (id: number): Promise<Entity> => {
    const response = await apiClient.get(`/entities/${id}`);
    return response.data;
  },

  // Search entities with filters
  searchEntities: async (params: EntitySearchParams): Promise<EntityListItem[]> => {
    const response = await apiClient.get('/entities/', { params });
    return response.data;
  },

  // Get entity relationships
  getEntityRelationships: async (
    id: number,
    relationshipType?: string
  ): Promise<RelationshipResponse> => {
    const params = relationshipType ? { relationship_type: relationshipType } : {};
    const response = await apiClient.get(`/entities/${id}/relationships`, { params });
    return response.data;
  },

  // Get entity graph
  getEntityGraph: async (
    id: number,
    maxDepth: number = 2,
    relationshipTypes?: string[]
  ): Promise<GraphData> => {
    const params: any = { max_depth: maxDepth };
    if (relationshipTypes && relationshipTypes.length > 0) {
      params.relationship_types = relationshipTypes.join(',');
    }
    const response = await apiClient.get(`/entities/${id}/graph`, { params });
    return response.data;
  },
};

export default entitiesApi;
