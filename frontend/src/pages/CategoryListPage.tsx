import { Alert, Button, Input, Space, Table } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateCategory, getCategory } from '../api/categoryApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';
import type { Category } from '../types/category';
import type { PaginationMeta } from '../types/api';
import { ROUTES } from '../config/paths';

export const CategoryListPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState<Pick<PaginationMeta, 'page' | 'page_size' | 'total_records'>>({ page: 1, page_size: 20, total_records: 0 });

  const loadCategories = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getCategory({ search, page: pagination.page, page_size: pagination.page_size });
      setCategories(response.data.data.results);
      setPagination((current) => ({ ...current, ...response.data.data.pagination }));
    } catch (loadError) {
      setCategories([]);
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadCategories(); }, [search, pagination.page, pagination.page_size]);

  const remove = (category: Category) => {
    confirmAction('Deactivate category', `Deactivate ${category.name}?`, async () => {
      try {
        await deactivateCategory(category.uuid);
        toast.success(`${category.name} was deactivated.`, 'Category deactivated');
        await loadCategories();
      } catch (error) {
        toast.error(getErrorMessage(error), 'Category deactivation failed');
      }
    });
  };

  return (
    <div>
      <PageHeader title="Categories" description="Browse and manage categories" extra={<Button type="primary" onClick={() => navigate(ROUTES.categoryNew)}>Add Category</Button>} />
      {error ? <Alert className="app-alert" type="error" message={error} showIcon /> : null}
      <Space className="list-toolbar">
        <Input.Search value={search} onChange={(e) => { setSearch(e.target.value); setPagination((p) => ({ ...p, page: 1 })); }} placeholder="Search category" />
      </Space>
      <Table
        loading={loading}
        dataSource={categories}
        rowKey="uuid"
        pagination={{ current: pagination.page, pageSize: pagination.page_size, total: pagination.total_records, showSizeChanger: true, onChange: (page, pageSize) => setPagination((p) => ({ ...p, page, page_size: pageSize })) }}
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Description', dataIndex: 'description', render: (value: string) => value || '-' },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(ROUTES.categoryDetail(record.uuid))}>View</Button><Button size="small" onClick={() => navigate(ROUTES.categoryEdit(record.uuid))}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
