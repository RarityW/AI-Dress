export interface ClothingItem {
  id: string;
  user_id: string;
  image_url: string;
  category: string;
  color: string;
  season: string;
  style: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Outfit {
  id: string;
  name: string;
  items: ClothingItem[];
  description: string;
}

export interface RecommendationRecord {
  id: string;
  outfit: Outfit;
  scene: string;
  score: number;
  reason: string;
}
