export interface ApiResponse<T> {
  code: number;
  success: boolean;
  message: string;
  data: T;
  request_id: string;
  timestamp: string;
}

export interface RecommendRequest {
  city?: string;
  scene?: string;
  style?: string;
}
