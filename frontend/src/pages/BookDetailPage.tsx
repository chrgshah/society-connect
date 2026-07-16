import { Card, Descriptions } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getBook } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import type { Book } from '../types/book';

export const BookDetailPage = () => {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      const response = await getBook(id);
      setBook(response.data.data);
    };
    void load();
  }, [id]);

  if (!book) return null;

  return (
    <div>
      <PageHeader title="Book Details" description="View the book details" />
      <Card>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="Title">{book.title}</Descriptions.Item>
          <Descriptions.Item label="ISBN">{book.isbn}</Descriptions.Item>
          <Descriptions.Item label="Author">{book.author || '-'}</Descriptions.Item>
          <Descriptions.Item label="Category">{book.category?.name || '-'}</Descriptions.Item>
          <Descriptions.Item label="Copies">{book.available_copies}/{book.total_copies}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};
