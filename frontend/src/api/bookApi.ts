import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Book, Category } from '../types/book';
import { API_PATHS } from '../config/paths';

export const getBooks = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Book>>>(API_PATHS.books, { params });
export const getBookOptions = (search = '') => apiClient.get<ApiResponse<Book[]>>(API_PATHS.bookOptions, { params: { search } });
export const createBook = (payload: Partial<Book> & { category_uuid?: string }) => apiClient.post<ApiResponse<Book>>(API_PATHS.books, payload);
export const updateBook = (uuid: string, payload: Partial<Book> & { category_uuid?: string }) => apiClient.patch<ApiResponse<Book>>(API_PATHS.book(uuid), payload);
export const deactivateBook = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(API_PATHS.book(uuid));
export const getBook = (uuid: string) => apiClient.get<ApiResponse<Book>>(API_PATHS.book(uuid));
export const getCategoryOptions = (search = '') => apiClient.get<ApiResponse<Category[]>>(API_PATHS.categoryOptions, { params: { search } });
