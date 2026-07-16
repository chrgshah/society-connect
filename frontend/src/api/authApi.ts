import apiClient from './client';
import type { ApiResponse } from '../types/api';
import type { AuthUser } from '../types/auth';

export const initializeCsrf = () => apiClient.get('/auth/csrf/');

export const login = async (username: string, password: string) => {
  await initializeCsrf();
  return apiClient.post('/auth/login/', { username, password });
};

export const refresh = () => apiClient.post('/auth/refresh/', {});

export const logout = () => apiClient.post('/auth/logout/', {});

export const getCurrentUser = async () => {
  const response = await apiClient.get<ApiResponse<AuthUser>>('/auth/me/');
  return response.data.data;
};
