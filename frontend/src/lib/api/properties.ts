// Property API service
import apiClient from './client';
import type { Property, PropertyListItem, PropertySearchParams, PropertyStatistics } from '../types/property';

export const propertiesApi = {
  // Get a specific property by ID
  getProperty: async (id: number): Promise<Property> => {
    const response = await apiClient.get(`/properties/${id}`);
    return response.data;
  },

  // Search properties with filters
  searchProperties: async (params: PropertySearchParams): Promise<PropertyListItem[]> => {
    const response = await apiClient.get('/properties/', { params });
    return response.data;
  },

  // Get property statistics by county
  getPropertyStatistics: async (county: string): Promise<PropertyStatistics> => {
    const response = await apiClient.get('/properties/statistics', {
      params: { county },
    });
    return response.data;
  },

  // Get property owners
  getPropertyOwners: async (id: number): Promise<any[]> => {
    const response = await apiClient.get(`/properties/${id}/owners`);
    return response.data;
  },
};

export default propertiesApi;
