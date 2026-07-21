import { Alert, Button, Card, Form, Input } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createCategory, getCategoryById, updateCategory } from '../api/categoryApi';
import { PageHeader } from '../components/PageHeader';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';

interface CategoryFormValues {
  name: string;
  description?: string;
}

export const CategoryFormPage = () => {
  const [form] = Form.useForm<CategoryFormValues>();
  const navigate = useNavigate();
  const toast = useToast();
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isEditing = Boolean(id);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        const response = await getCategoryById(id);
        form.setFieldsValue(response.data.data);
      } catch (loadError) {
        setError(getErrorMessage(loadError));
      }
    };
    void load();
  }, [id, form]);

  const onFinish = async (values: CategoryFormValues) => {
    setLoading(true);
    setError('');
    const payload = { name: values.name.trim(), description: values.description?.trim() || '' };
    try {
      if (id) {
        await updateCategory(id, payload);
        toast.success('The category was updated.', 'Category updated');
      } else {
        await createCategory(payload);
        toast.success('The category was added.', 'Category added');
      }
      navigate('/categories');
    } catch (submitError) {
      const message = getErrorMessage(submitError);
      setError(message);
      toast.error(message, isEditing ? 'Category update failed' : 'Category creation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title={isEditing ? 'Edit Category' : 'Create Category'} description="Add or edit a book category" />
      <Card>
        {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} /> : null}
        <Form form={form} layout="vertical" onFinish={onFinish} onValuesChange={() => { if (error) setError(''); }}>
          <Form.Item label="Name" name="name" rules={[{ required: true, whitespace: true, message: 'Please enter a category name' }]}>
            <Input maxLength={200} />
          </Form.Item>
          <Form.Item label="Description" name="description"><Input.TextArea rows={4} /></Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>Save</Button>
        </Form>
      </Card>
    </div>
  );
};
