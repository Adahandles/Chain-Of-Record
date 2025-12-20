// Custom hooks for entity data
'use client';

import { useQuery } from '@tanstack/react-query';
import { entitiesApi } from '../api/entities';
import type { EntitySearchParams } from '../types/entity';

// Hook to get a single entity
export function useEntity(id: number | null) {
  return useQuery({
    queryKey: ['entity', id],
    queryFn: () => (id ? entitiesApi.getEntity(id) : null),
    enabled: !!id,
  });
}

// Hook to search entities
export function useEntities(params: EntitySearchParams) {
  return useQuery({
    queryKey: ['entities', params],
    queryFn: () => entitiesApi.searchEntities(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook to get entity relationships
export function useEntityRelationships(id: number | null, relationshipType?: string) {
  return useQuery({
    queryKey: ['entity-relationships', id, relationshipType],
    queryFn: () => (id ? entitiesApi.getEntityRelationships(id, relationshipType) : null),
    enabled: !!id,
  });
}

// Hook to get entity graph
export function useEntityGraph(
  id: number | null,
  maxDepth: number = 2,
  relationshipTypes?: string[]
) {
  return useQuery({
    queryKey: ['entity-graph', id, maxDepth, relationshipTypes],
    queryFn: () => (id ? entitiesApi.getEntityGraph(id, maxDepth, relationshipTypes) : null),
    enabled: !!id,
  });
}
