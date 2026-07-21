import apiClient from './client';
import type { ApiResponse } from '../types/api';
import type { AuthUser } from '../types/auth';
import { API_PATHS } from '../config/paths';

export const initializeCsrf = () => apiClient.get(API_PATHS.csrf);

export const login = async (username: string, password: string) => {
  await initializeCsrf();
  return apiClient.post(API_PATHS.login, { username, password });
};

export const refresh = () => apiClient.post(API_PATHS.refresh, {});

export const logout = () => apiClient.post(API_PATHS.logout, {});

export const getCurrentUser = async () => {
  const response = await apiClient.get<ApiResponse<AuthUser>>(API_PATHS.currentUser);
  return response.data.data;
};
