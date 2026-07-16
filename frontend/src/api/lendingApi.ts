import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Lending } from '../types/lending';

export const borrowBook = (payload: { member_uuid: string; book_uuid: string; due_at?: string; notes?: string }) => apiClient.post<ApiResponse<Lending>>('/lending/borrow/', payload);
export const returnBook = (uuid: string) => apiClient.post<ApiResponse<Lending>>(`/lending/${uuid}/return/`);
export const getLendings = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Lending>>>('/lending/', { params });
export const getMemberBorrowedBooks = (memberUuid: string) => apiClient.get<ApiResponse<Lending[]>>(`/members/${memberUuid}/borrowed-books/`);
export const getOverdueLendings = () => apiClient.get<ApiResponse<Lending[]>>('/lending/overdue/');
