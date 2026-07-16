import apiClient from './client';
import type { ApiResponse } from '../types/api';

export const getDashboardSummary = () => apiClient.get<ApiResponse<Record<string, number>>>('/dashboard/summary/');
