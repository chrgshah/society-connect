import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Member } from '../types/member';

export const getMembers = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Member>>>('/members/', { params });
export const createMember = (payload: Partial<Member>) => apiClient.post<ApiResponse<Member>>('/members/', payload);
export const updateMember = (uuid: string, payload: Partial<Member>) => apiClient.patch<ApiResponse<Member>>(`/members/${uuid}/`, payload);
export const deactivateMember = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(`/members/${uuid}/`);
export const getMember = (uuid: string) => apiClient.get<ApiResponse<Member>>(`/members/${uuid}/`);
