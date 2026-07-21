import apiClient from './client';
import type { ApiResponse } from '../types/api';
import { API_PATHS } from '../config/paths';

export const getDashboardSummary = (params?: { from_date: string; to_date: string }) =>
  apiClient.get<ApiResponse<Record<string, number>>>(API_PATHS.dashboardSummary, { params });
