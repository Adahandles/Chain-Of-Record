// Property types from backend schemas
import type { Address } from './entity';

export interface Property {
  id: number;
  parcel_id: string;
  county: string;
  jurisdiction?: string | null;
  land_use_code?: string | null;
  acreage?: number | null;
  last_sale_date?: string | null;
  last_sale_price?: number | null;
  market_value?: number | null;
  assessed_value?: number | null;
  homestead_exempt?: string | null;
  tax_year?: string | null;
  appraiser_url?: string | null;
  created_at: string;
  updated_at: string;
  situs_address?: Address | null;
}

export interface PropertyListItem {
  id: number;
  parcel_id: string;
  county: string;
  land_use_code?: string | null;
  acreage?: number | null;
  last_sale_price?: number | null;
  market_value?: number | null;
}

export interface PropertySearchParams {
  county?: string;
  land_use_code?: string;
  min_value?: number;
  max_value?: number;
  min_acres?: number;
  limit?: number;
}

export interface PropertyStatistics {
  county: string;
  total_properties: number;
  avg_sale_price?: number | null;
  median_sale_price?: number | null;
  total_sales: number;
}
