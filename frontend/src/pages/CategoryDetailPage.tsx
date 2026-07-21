import { Alert, Button, Card, Descriptions } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getCategoryById } from '../api/categoryApi';
import { PageHeader } from '../components/PageHeader';
import { getErrorMessage } from '../utils/errors';
import type { Category } from '../types/category';

export const CategoryDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [category, setCategory] = useState<Category | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        const response = await getCategoryById(id);
        setCategory(response.data.data);
      } catch (loadError) {
        setError(getErrorMessage(loadError));
      }
    };
    void load();
  }, [id]);

  if (error) return <div><PageHeader title="Category Details" description="View category details" /><Alert type="error" message={error} showIcon /></div>;
  if (!category) return null;

  return (
    <div>
      <PageHeader title="Category Details" description="View category details" extra={<Button type="primary" onClick={() => navigate(`/categories/${category.uuid}/edit`)}>Edit</Button>} />
      <Card>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="Name">{category.name}</Descriptions.Item>
          <Descriptions.Item label="Description">{category.description || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};
