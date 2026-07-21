import apiClient from './client';
import type { ApiResponse } from '../types/api';
import { API_PATHS } from '../config/paths';

export const getDashboardSummary = () => apiClient.get<ApiResponse<Record<string, number>>>(API_PATHS.dashboardSummary);
