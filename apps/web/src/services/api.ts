import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { ApiResponse } from '../types/api';
import {
  ClothingItem,
  ClothingItemCreate,
  ClothingListResponse,
  ImageUploadResponse,
  RecommendationRequest,
  RecommendationResponse
} from '../types/clothing';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  config.headers['X-Request-ID'] = uuidv4();
  return config;
});

api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const getHealth = (): Promise<ApiResponse<any>> => {
  return api.get('/api/v1/health');
};

export const uploadClothingImage = (file: File): Promise<ApiResponse<ImageUploadResponse>> => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/clothing/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  });
};

export const createClothing = (data: ClothingItemCreate): Promise<ApiResponse<ClothingItem>> => {
  return api.post('/api/v1/clothing', data);
};

export const getClothingList = (params?: {
  page?: number;
  page_size?: number;
  category?: string;
  style?: string;
  season?: string;
}): Promise<ApiResponse<ClothingListResponse>> => {
  return api.get('/api/v1/clothing', { params });
};

export const getClothingDetail = (id: string): Promise<ApiResponse<ClothingItem>> => {
  return api.get(`/api/v1/clothing/${id}`);
};

export const deleteClothing = (id: string): Promise<ApiResponse<null>> => {
  return api.delete(`/api/v1/clothing/${id}`);
};

export const getRecommendations = (params: RecommendationRequest): Promise<ApiResponse<RecommendationResponse>> => {
  return api.post('/api/v1/recommendations', params);
};

export const submitRecommendationFeedback = (recordId: string, rating: number): Promise<ApiResponse<any>> => {
  return api.post(`/api/v1/recommendations/${recordId}/feedback`, { rating });
};

export const getRecommendationHistory = (): Promise<ApiResponse<any[]>> => {
  return api.get('/api/v1/recommendations/history');
};

export const getWeather = (city: string): Promise<ApiResponse<any>> => {
  return api.get('/api/v1/weather', { params: { city } });
};

export default api;
