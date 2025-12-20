// Custom hooks for property data
'use client';

import { useQuery } from '@tanstack/react-query';
import { propertiesApi } from '../api/properties';
import type { PropertySearchParams } from '../types/property';

// Hook to get a single property
export function useProperty(id: number | null) {
  return useQuery({
    queryKey: ['property', id],
    queryFn: () => (id ? propertiesApi.getProperty(id) : null),
    enabled: !!id,
  });
}

// Hook to search properties
export function useProperties(params: PropertySearchParams) {
  return useQuery({
    queryKey: ['properties', params],
    queryFn: () => propertiesApi.searchProperties(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook to get property statistics
export function usePropertyStatistics(county: string) {
  return useQuery({
    queryKey: ['property-statistics', county],
    queryFn: () => propertiesApi.getPropertyStatistics(county),
    enabled: !!county,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook to get property owners
export function usePropertyOwners(id: number | null) {
  return useQuery({
    queryKey: ['property-owners', id],
    queryFn: () => (id ? propertiesApi.getPropertyOwners(id) : null),
    enabled: !!id,
  });
}
