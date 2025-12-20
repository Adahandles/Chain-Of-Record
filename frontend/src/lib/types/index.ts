// Common types and utilities

export interface ApiError {
  detail: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface Relationship {
  id: number;
  direction: 'outgoing' | 'incoming';
  type: string;
  from_type: string;
  from_id: number;
  to_type: string;
  to_id: number;
  source_system: string;
  start_date?: string | null;
  end_date?: string | null;
  confidence?: number | null;
}

export interface RelationshipResponse {
  entity_id: number;
  total_relationships: number;
  relationships: Relationship[];
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export interface User {
  id: number;
  email: string;
  name?: string;
  role: 'user' | 'admin';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
