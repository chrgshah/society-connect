import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Member } from '../types/member';
import { API_PATHS } from '../config/paths';

export const getMembers = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Member>>>(API_PATHS.members, { params });
export const getMemberOptions = (search = '') => apiClient.get<ApiResponse<Member[]>>(API_PATHS.memberOptions, { params: { search } });
export const createMember = (payload: Partial<Member>) => apiClient.post<ApiResponse<Member>>(API_PATHS.members, payload);
export const updateMember = (uuid: string, payload: Partial<Member>) => apiClient.patch<ApiResponse<Member>>(API_PATHS.member(uuid), payload);
export const deactivateMember = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(API_PATHS.member(uuid));
export const getMember = (uuid: string) => apiClient.get<ApiResponse<Member>>(API_PATHS.member(uuid));
