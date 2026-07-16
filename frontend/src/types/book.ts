export interface Category {
  uuid: string;
  name: string;
  description: string;
}

export interface Book {
  uuid: string;
  isbn: string;
  title: string;
  author: string;
  category?: Category;
  publisher?: string;
  published_year?: number;
  description?: string;
  total_copies: number;
  available_copies: number;
  shelf_location?: string;
  is_active: boolean;
}
