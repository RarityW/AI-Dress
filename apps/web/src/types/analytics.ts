export interface MetricOverview {
  total_items: number;
  total_outfits: number;
  utilization_rate: number;
  capsule_score: number;
  capsule_level: string;
}

export interface DistributionItem {
  key: string;
  label: string;
  count: number;
  percentage: number;
  color?: string;
}

export interface ColorDistributionItem {
  color_name: string;
  hex_code: string;
  count: number;
  percentage: number;
  is_neutral: boolean;
}

export interface VersatileItem {
  id: string;
  category: string;
  sub_category: string;
  primary_color: string;
  style: string;
  image_url: string;
  match_count: number;
  versatility_score: number;
  highlight_reason: string;
}

export interface IdleItem {
  id: string;
  category: string;
  sub_category: string;
  primary_color: string;
  style: string;
  image_url: string;
  temp_range: string;
  idle_days: number;
  revive_suggestion: string;
}

export interface WardrobeDiagnosis {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  purchase_suggestions: string[];
}

export interface AnalyticsOverviewResponse {
  metrics: MetricOverview;
  categories: DistributionItem[];
  seasons: DistributionItem[];
  styles: DistributionItem[];
  colors: ColorDistributionItem[];
  neutral_ratio: number;
  versatile_items: VersatileItem[];
  idle_items: IdleItem[];
  diagnosis: WardrobeDiagnosis;
}
