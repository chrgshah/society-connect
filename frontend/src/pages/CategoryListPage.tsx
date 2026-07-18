import { Alert, Button, Input, Space, Table } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateCategory, getCategory } from '../api/categoryApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';
import type { Category } from '../types/category';

export const CategoryListPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');

  const loadCategories = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getCategory({ search, page: 1, page_size: 20 });
      setCategories(response.data.data.results);
    } catch (loadError) {
      setCategories([]);
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadCategories(); }, [search]);

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
      <PageHeader title="Categories" description="Browse and manage categories" extra={<Button type="primary" onClick={() => navigate('/categories/new')}>Add Category</Button>} />
      {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} /> : null}
      <Space style={{ marginBottom: 16 }}>
        <Input.Search value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search category" />
      </Space>
      <Table
        loading={loading}
        dataSource={categories}
        rowKey="uuid"
        columns={[
          { title: 'Name', dataIndex: 'name' },
          { title: 'Description', dataIndex: 'description', render: (value: string) => value || '-' },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(`/categories/${record.uuid}`)}>View</Button><Button size="small" onClick={() => navigate(`/categories/${record.uuid}/edit`)}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
