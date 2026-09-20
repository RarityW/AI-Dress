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

/** VLM 视觉大模型识别结果 */
export interface VLMAnalysisResponse {
  category: string;
  sub_category: string;
  primary_color: string;
  secondary_color: string | null;
  style: string;
  thickness: string;
  season: string[];
  temp_min: number;
  temp_max: number;
  raw_vlm_attributes?: Record<string, any>;
  confidence_score?: number;
}

/** 搭配中单品详情 */
export interface OutfitItemDetail {
  id: string;
  category: string;
  sub_category: string;
  primary_color: string;
  secondary_color: string | null;
  style: string;
  thickness: string;
  image_url: string;
  temp_min: number;
  temp_max: number;
}

/** 评分维度明细 */
export interface ScoreBreakdown {
  weather_score: number;
  style_score: number;
  scene_score: number;
  color_score: number;
  overall_score: number;
}

/** 一套穿搭推荐结果 */
export interface OutfitRecommendation {
  outfit_id: string;
  items: OutfitItemDetail[];
  scores: ScoreBreakdown;
  reason: string;
}

/** 推荐请求参数 */
export interface RecommendationRequest {
  city: string;
  temperature?: number;
  weather_condition?: string;
  scene: string;
  target_style: string;
  top_k?: number;
}

/** 推荐响应结果 */
export interface RecommendationResponse {
  record_id?: string | null;
  city: string;
  current_temp: number;
  weather_condition: string;
  scene: string;
  target_style: string;
  total_candidates: number;
  recommendations: OutfitRecommendation[];
}

/** 穿搭方案实体 */
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

/** 推荐历史记录 */
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

/** AI 模特试穿生图请求 */
export interface TryOnRequest {
  outfit_id: string;
  items: Array<{
    sub_category: string;
    primary_color: string;
    image_url?: string;
  }>;
  gender?: string;
  scene?: string;
  target_style?: string;
}

/** AI 模特试穿生图结果 */
export interface TryOnResponse {
  outfit_id: string;
  image_url: string;
  prompt: string;
  source: string;
}

