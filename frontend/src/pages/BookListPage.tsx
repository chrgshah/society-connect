import { Alert, Button, Input, Space, Table, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateBook, getBooks } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';
import type { Book } from '../types/book';
import type { PaginationMeta } from '../types/api';
import { ROUTES } from '../config/paths';

export const BookListPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState<Pick<PaginationMeta, 'page' | 'page_size' | 'total_records'>>({ page: 1, page_size: 20, total_records: 0 });

  const loadBooks = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getBooks({ search, page: pagination.page, page_size: pagination.page_size });
      setBooks(response.data.data.results);
      setPagination((current) => ({ ...current, ...response.data.data.pagination }));
    } catch (loadError) {
      setBooks([]);
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadBooks(); }, [search, pagination.page, pagination.page_size]);

  const remove = (book: Book) => {
    confirmAction('Deactivate book', `Deactivate ${book.title}?`, async () => {
      try {
        await deactivateBook(book.uuid);
        toast.success(`${book.title} was deactivated.`, 'Book deactivated');
        await loadBooks();
      } catch (error) {
        toast.error(getErrorMessage(error), 'Book deactivation failed');
      }
    });
  };

  return (
    <div>
      <PageHeader title="Books" description="Browse and manage books" extra={<Button type="primary" onClick={() => navigate(ROUTES.bookNew)}>Add Book</Button>} />
      {error ? <Alert className="app-alert" type="error" message={error} showIcon /> : null}
      <Space className="list-toolbar">
        <Input.Search value={search} onChange={(e) => { setSearch(e.target.value); setPagination((p) => ({ ...p, page: 1 })); }} placeholder="Search books" />
      </Space>
      <Table
        loading={loading}
        dataSource={books}
        rowKey="uuid"
        pagination={{ current: pagination.page, pageSize: pagination.page_size, total: pagination.total_records, showSizeChanger: true, onChange: (page, pageSize) => setPagination((p) => ({ ...p, page, page_size: pageSize })) }}
        columns={[
          { title: 'ISBN', dataIndex: 'isbn' },
          { title: 'Title', dataIndex: 'title' },
          { title: 'Author', dataIndex: 'author' },
          { title: 'Category', render: (record) => record.category?.name || '-' },
          { title: 'Copies', render: (record) => `${record.available_copies}/${record.total_copies}` },
          { title: 'Availability', render: (record) => <Tag color={record.available_copies > 0 ? 'green' : 'red'}>{record.available_copies > 0 ? 'Available' : 'Unavailable'}</Tag> },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(ROUTES.bookDetail(record.uuid))}>View</Button><Button size="small" onClick={() => navigate(ROUTES.bookEdit(record.uuid))}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
