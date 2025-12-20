// Risk scoring types from backend schemas

export interface RuleDetail {
  name: string;
  weight: number;
  category: string;
  description: string;
}

export interface ScoringContext {
  property_count: number;
  entity_age_days?: number | null;
  agent_entity_count: number;
  address_entity_count: number;
}

export interface RiskScore {
  entity_id: number;
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  flags: string[];
  rule_details: RuleDetail[];
  context: ScoringContext;
  calculated_at?: string | null;
}

export interface HistoricalScore {
  entity_id: number;
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  flags: string[];
  calculated_at: string;
}

export interface BatchScoreRequest {
  entity_ids: number[];
}

export interface BatchScoreResponse {
  total_requested: number;
  total_scored: number;
  scores: RiskScore[];
}

export interface HighRiskEntity {
  entity: {
    id: number;
    legal_name: string;
    type: string;
    jurisdiction?: string | null;
    status?: string | null;
  };
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  flags: string[];
  calculated_at: string;
}

export interface ScoringStatistics {
  total_entities_scored: number;
  average_score?: number | null;
  grade_distribution: Record<string, number>;
}
