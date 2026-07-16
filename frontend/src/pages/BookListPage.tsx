import { Button, Input, Select, Space, Table, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateBook, getBooks } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import type { Book } from '../types/book';

export const BookListPage = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  const loadBooks = async () => {
    setLoading(true);
    try {
      const response = await getBooks({ search, page: 1, page_size: 20 });
      setBooks(response.data.data.results);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadBooks(); }, [search]);

  const remove = (book: Book) => {
    confirmAction('Deactivate book', `Deactivate ${book.title}?`, async () => {
      await deactivateBook(book.uuid);
      void loadBooks();
    });
  };

  return (
    <div>
      <PageHeader title="Books" description="Browse and manage books" extra={<Button type="primary" onClick={() => navigate('/books/new')}>Add Book</Button>} />
      <Space style={{ marginBottom: 16 }}>
        <Input.Search value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search books" />
      </Space>
      <Table
        loading={loading}
        dataSource={books}
        rowKey="uuid"
        columns={[
          { title: 'ISBN', dataIndex: 'isbn' },
          { title: 'Title', dataIndex: 'title' },
          { title: 'Author', dataIndex: 'author' },
          { title: 'Category', render: (record) => record.category?.name || '-' },
          { title: 'Copies', render: (record) => `${record.available_copies}/${record.total_copies}` },
          { title: 'Availability', render: (record) => <Tag color={record.available_copies > 0 ? 'green' : 'red'}>{record.available_copies > 0 ? 'Available' : 'Unavailable'}</Tag> },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(`/books/${record.uuid}`)}>View</Button><Button size="small" onClick={() => navigate(`/books/${record.uuid}/edit`)}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
