import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { ApiResponse, RecommendRequest } from '../types/api';
import { ClothingItem, RecommendationRecord } from '../types/clothing';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
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

export const getClothingList = (): Promise<ApiResponse<ClothingItem[]>> => {
  return api.get('/api/v1/clothing');
};

export const analyzeClothing = (file: File): Promise<ApiResponse<ClothingItem>> => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/v1/clothing/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getRecommendations = (params: RecommendRequest): Promise<ApiResponse<RecommendationRecord[]>> => {
  return api.post('/api/v1/recommendations', params);
};

export const getWeather = (city: string): Promise<ApiResponse<any>> => {
  return api.get('/api/v1/weather', { params: { city } });
};

export default api;
