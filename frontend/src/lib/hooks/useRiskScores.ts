// Custom hooks for risk scoring data
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { scoresApi } from '../api/scores';

// Hook to get/calculate entity score
export function useEntityScore(entityId: number | null) {
  return useQuery({
    queryKey: ['entity-score', entityId],
    queryFn: () => (entityId ? scoresApi.scoreEntity(entityId) : null),
    enabled: !!entityId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Hook to get latest stored score
export function useLatestScore(entityId: number | null) {
  return useQuery({
    queryKey: ['latest-score', entityId],
    queryFn: () => (entityId ? scoresApi.getLatestScore(entityId) : null),
    enabled: !!entityId,
    retry: false, // Don't retry if no score exists
  });
}

// Hook to get score history
export function useScoreHistory(entityId: number | null, limit: number = 10) {
  return useQuery({
    queryKey: ['score-history', entityId, limit],
    queryFn: () => (entityId ? scoresApi.getScoreHistory(entityId, limit) : null),
    enabled: !!entityId,
  });
}

// Hook to get high-risk entities
export function useHighRiskEntities(grade: 'A' | 'B' | 'C' | 'D' | 'F' = 'F', limit: number = 100) {
  return useQuery({
    queryKey: ['high-risk-entities', grade, limit],
    queryFn: () => scoresApi.getHighRiskEntities(grade, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook to get scoring statistics
export function useScoringStatistics() {
  return useQuery({
    queryKey: ['scoring-statistics'],
    queryFn: () => scoresApi.getStatistics(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook for batch scoring
export function useBatchScore() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (entityIds: number[]) => scoresApi.batchScore(entityIds),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['entity-score'] });
      queryClient.invalidateQueries({ queryKey: ['high-risk-entities'] });
      queryClient.invalidateQueries({ queryKey: ['scoring-statistics'] });
    },
  });
}
