import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Category } from '../types/category';

export const getCategories = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Category>>>('/categories/', { params });
export const getCategory = getCategories;
export const createCategory = (payload: Partial<Category>) => apiClient.post<ApiResponse<Category>>('/categories/', payload);
export const updateCategory = (uuid: string, payload: Partial<Category>) => apiClient.patch<ApiResponse<Category>>(`/categories/${uuid}/`, payload);
export const deactivateCategory = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(`/categories/${uuid}/`);
export const getCategoryById = (uuid: string) => apiClient.get<ApiResponse<Category>>(`/categories/${uuid}/`);
