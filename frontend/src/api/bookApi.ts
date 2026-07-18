import apiClient from './client';
import type { ApiResponse, PaginatedData } from '../types/api';
import type { Book, Category } from '../types/book';

export const getBooks = (params?: Record<string, unknown>) => apiClient.get<ApiResponse<PaginatedData<Book>>>('/books/', { params });
export const createBook = (payload: Partial<Book> & { category_uuid?: string }) => apiClient.post<ApiResponse<Book>>('/books/', payload);
export const updateBook = (uuid: string, payload: Partial<Book> & { category_uuid?: string }) => apiClient.patch<ApiResponse<Book>>(`/books/${uuid}/`, payload);
export const deactivateBook = (uuid: string) => apiClient.delete<ApiResponse<unknown>>(`/books/${uuid}/`);
export const getBook = (uuid: string) => apiClient.get<ApiResponse<Book>>(`/books/${uuid}/`);
export const getCategories = () => apiClient.get<ApiResponse<PaginatedData<Category>>>('/categories/', { params: { page_size: 100 } });
