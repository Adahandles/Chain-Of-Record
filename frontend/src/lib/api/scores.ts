// Scoring API service
import apiClient from './client';
import type {
  RiskScore,
  HistoricalScore,
  BatchScoreResponse,
  HighRiskEntity,
  ScoringStatistics,
} from '../types/score';

export const scoresApi = {
  // Score a specific entity (calculates new score)
  scoreEntity: async (entityId: number): Promise<RiskScore> => {
    const response = await apiClient.get(`/scores/entity/${entityId}`);
    return response.data;
  },

  // Get latest stored score for an entity
  getLatestScore: async (entityId: number): Promise<RiskScore> => {
    const response = await apiClient.get(`/scores/entity/${entityId}/latest`);
    return response.data;
  },

  // Get historical scores for an entity
  getScoreHistory: async (entityId: number, limit: number = 10): Promise<HistoricalScore[]> => {
    const response = await apiClient.get(`/scores/entity/${entityId}/history`, {
      params: { limit },
    });
    return response.data;
  },

  // Batch score multiple entities
  batchScore: async (entityIds: number[]): Promise<BatchScoreResponse> => {
    const response = await apiClient.post('/scores/batch', { entity_ids: entityIds });
    return response.data;
  },

  // Get high-risk entities
  getHighRiskEntities: async (
    grade: 'A' | 'B' | 'C' | 'D' | 'F' = 'F',
    limit: number = 100
  ): Promise<{ grade_threshold: string; total_entities: number; entities: HighRiskEntity[] }> => {
    const response = await apiClient.get('/scores/high-risk', {
      params: { grade, limit },
    });
    return response.data;
  },

  // Get scoring statistics
  getStatistics: async (): Promise<ScoringStatistics> => {
    const response = await apiClient.get('/scores/statistics');
    return response.data;
  },
};

export default scoresApi;
