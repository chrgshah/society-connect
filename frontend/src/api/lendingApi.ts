import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Lending } from '../types/lending';
import { API_PATHS } from '../config/paths';

export const borrowBook = (payload: { member_uuid: string; book_uuid: string; due_at?: string; notes?: string }) => apiClient.post<ApiResponse<Lending>>(API_PATHS.borrow, payload);
export const returnBook = (uuid: string) => apiClient.post<ApiResponse<Lending>>(API_PATHS.returnBook(uuid));
export const getLendings = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Lending>>>(API_PATHS.lendings, { params });
export const getMemberBorrowedBooks = (memberUuid: string) => apiClient.get<ApiResponse<Lending[]>>(API_PATHS.memberBorrowedBooks(memberUuid));
export const getOverdueLendings = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Lending>>>(API_PATHS.overdue, { params });
