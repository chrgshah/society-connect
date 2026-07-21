import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Category } from '../types/category';
import { API_PATHS } from '../config/paths';

export const getCategories = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Category>>>(API_PATHS.categories, { params });
export const getCategoryOptions = (search = '') => apiClient.get<ApiResponse<Category[]>>(API_PATHS.categoryOptions, { params: { search } });
export const getCategory = getCategories;
export const createCategory = (payload: Partial<Category>) => apiClient.post<ApiResponse<Category>>(API_PATHS.categories, payload);
export const updateCategory = (uuid: string, payload: Partial<Category>) => apiClient.patch<ApiResponse<Category>>(API_PATHS.category(uuid), payload);
export const deactivateCategory = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(API_PATHS.category(uuid));
export const getCategoryById = (uuid: string) => apiClient.get<ApiResponse<Category>>(API_PATHS.category(uuid));
