export interface User {
  id: string;
  username: string;
  email: string;
  created_at?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserPreferences {
  preferred_styles: string[];
  avoided_colors: string[];
  custom_weights: {
    weather?: number;
    style?: number;
    scene?: number;
    color?: number;
    preference?: number;
    [key: string]: number | undefined;
  };
}

export interface OutfitItemBrief {
  id: string;
  image_url?: string;
  category?: string;
  primary_color?: string;
  style?: string;
}

export interface Outfit {
  id: string;
  name: string;
  occasion: string;
  season: string;
  item_ids: string[];
  items: OutfitItemBrief[];
  overall_score?: number;
  created_at?: string;
}

export interface OutfitListResponse {
  items: Outfit[];
  total: number;
}
