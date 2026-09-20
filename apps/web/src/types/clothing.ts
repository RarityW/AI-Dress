/** 衣物单品 */
export interface ClothingItem {
  id: string;
  user_id: string;
  image_url: string;
  category: string;
  sub_category: string;
  primary_color: string;
  secondary_color: string | null;
  style: string;
  thickness: string;
  season: string[];
  temp_min: number;
  temp_max: number;
  raw_vlm_attributes: Record<string, any> | null;
  created_at: string;
}

/** 衣物列表响应 */
export interface ClothingListResponse {
  items: ClothingItem[];
  total: number;
  page: number;
  page_size: number;
}

/** 创建衣物请求 */
export interface ClothingItemCreate {
  category: string;
  sub_category: string;
  primary_color: string;
  secondary_color?: string;
  style: string;
  thickness: string;
  season: string[];
  temp_min: number;
  temp_max: number;
  image_url?: string;
  raw_vlm_attributes?: Record<string, any>;
}

/** 更新衣物请求 */
export interface ClothingItemUpdate {
  category?: string;
  sub_category?: string;
  primary_color?: string;
  secondary_color?: string;
  style?: string;
  thickness?: string;
  season?: string[];
  temp_min?: number;
  temp_max?: number;
}

/** 图片上传响应 */
export interface ImageUploadResponse {
  image_url: string;
  filename: string;
}

/** 穿搭方案 */
export interface Outfit {
  id: string;
  user_id: string;
  name: string;
  occasion: string;
  season: string;
  item_ids: string[];
  overall_score: number;
  created_at: string;
}

/** 推荐记录 */
export interface RecommendationRecord {
  id: string;
  user_id: string;
  city: string;
  current_temp: number;
  weather_condition: string;
  scene: string;
  target_style: string;
  candidate_outfits: any[];
  ai_reason: string;
  feedback_rating: number | null;
  created_at: string;
}
