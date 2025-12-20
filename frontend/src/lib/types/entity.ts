// TypeScript types generated from backend Pydantic schemas

export interface Address {
  id: number;
  line1: string;
  line2?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  county?: string | null;
  country: string;
}

export interface Person {
  id: number;
  full_name: string;
}

export interface Entity {
  id: number;
  external_id?: string | null;
  source_system: string;
  type: string;
  legal_name: string;
  jurisdiction?: string | null;
  status?: string | null;
  formation_date?: string | null;
  ein_available?: boolean | null;
  ein_verified?: boolean | null;
  created_at: string;
  updated_at: string;
  registered_agent?: Person | null;
  primary_address?: Address | null;
}

export interface EntityListItem {
  id: number;
  legal_name: string;
  type: string;
  jurisdiction?: string | null;
  status?: string | null;
  formation_date?: string | null;
}

export interface EntitySearchParams {
  name?: string;
  jurisdiction?: string;
  entity_type?: string;
  status?: string;
  limit?: number;
}

export interface EntityCreate {
  external_id: string;
  source_system: string;
  type: string;
  legal_name: string;
  jurisdiction?: string;
  status?: string;
  formation_date?: string;
  ein_available?: boolean;
  ein_verified?: boolean;
}
