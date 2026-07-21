import { Alert, Button, Card, Form, Input, InputNumber, Select, Switch } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createBook, getBook, getCategoryOptions, updateBook } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';
import type { Category } from '../types/book';
import { ROUTES } from '../config/paths';
import { useDebouncedValue } from '../hooks/useDebouncedValue';

interface BookFormValues {
  isbn: string;
  title: string;
  author: string;
  category_uuid: string;
  publisher?: string;
  published_year?: number;
  description?: string;
  total_copies: number;
  available_copies: number;
  shelf_location?: string;
  is_active: boolean;
}

export const BookFormPage = () => {
  const [form] = Form.useForm<BookFormValues>();
  const navigate = useNavigate();
  const toast = useToast();
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [categorySearch, setCategorySearch] = useState('');
  const debouncedCategorySearch = useDebouncedValue(categorySearch);

  useEffect(() => {
    const load = async () => {
      try {
        if (id && id !== 'new') {
          const response = await getBook(id);
          const book = response.data.data;
          if (book.category) setCategories([book.category]);
          form.setFieldsValue({
            ...book,
            category_uuid: book.category?.uuid,
          } as BookFormValues);
        }
      } catch (err) {
        setError(getErrorMessage(err));
      }
    };
    void load();
  }, [id, form]);

  useEffect(() => {
    let cancelled = false;
    const loadCategories = async () => {
      setCategoriesLoading(true);
      try {
        const response = await getCategoryOptions(debouncedCategorySearch.trim());
        if (!cancelled) setCategories(response.data.data);
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setCategoriesLoading(false);
      }
    };
    void loadCategories();
    return () => { cancelled = true; };
  }, [debouncedCategorySearch]);

  const onFinish = async (values: BookFormValues) => {
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...values,
        isbn: values.isbn.trim(),
        title: values.title.trim(),
        author: values.author.trim(),
        category_uuid: values.category_uuid.trim(),
        publisher: values.publisher?.trim() || '',
        description: values.description?.trim() || '',
        shelf_location: values.shelf_location?.trim() || '',
      };
      if (id && id !== 'new') {
        await updateBook(id, payload);
        toast.success('The book details were updated.', 'Book updated');
      } else {
        await createBook(payload);
        toast.success('The new book was added to the library.', 'Book added');
      }
      navigate(ROUTES.books);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      toast.error(message, id && id !== 'new' ? 'Book update failed' : 'Book creation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title={id && id !== 'new' ? 'Edit Book' : 'Create Book'} description="Add or edit a library book" />
      <Card>
        {error ? <Alert type="error" message={error} showIcon className="app-alert" /> : null}
        <Form
          form={form}
          layout="vertical"
          initialValues={{ total_copies: 1, available_copies: 1, is_active: true }}
          onFinish={onFinish}
          onValuesChange={() => {
            if (error) setError('');
          }}
        >
          <Form.Item label="ISBN" name="isbn" rules={[{ required: true, whitespace: true, message: 'Please enter ISBN' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Title" name="title" rules={[{ required: true, whitespace: true, message: 'Please enter Title' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Author" name="author" rules={[{ required: true, whitespace: true, message: 'Please enter Author' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Category" name="category_uuid" rules={[{ required: true, message: 'Please select Category' }]}>
            <Select
              loading={categoriesLoading}
              placeholder="Select a category"
              showSearch
              filterOption={false}
              onSearch={setCategorySearch}
              notFoundContent={categoriesLoading ? 'Loading categories...' : 'No categories found'}
              options={categories.map((category) => ({
                label: category.name,
                value: category.uuid,
              }))}
            />
          </Form.Item>
          <Form.Item label="Publisher" name="publisher">
            <Input />
          </Form.Item>
          <Form.Item label="Published Year" name="published_year">
            <InputNumber min={0} max={new Date().getFullYear()} className="full-width-control" />
          </Form.Item>
          <Form.Item label="Description" name="description" rules={[{ max: 2500, message: 'Description cannot exceed 2,500 characters' }]}>
            <Input.TextArea maxLength={2500} showCount />
          </Form.Item>
          <Form.Item label="Total Copies" name="total_copies" rules={[{ required: true, message: 'Please enter Total Copies' }]}>
            <InputNumber min={1} className="full-width-control" />
          </Form.Item>
          <Form.Item label="Available Copies" name="available_copies" dependencies={['total_copies']} rules={[{ required: true, message: 'Please enter Available Copies' }, ({ getFieldValue }) => ({ validator(_, value) { return value <= getFieldValue('total_copies') ? Promise.resolve() : Promise.reject(new Error('Available copies cannot exceed total copies')); } })]}>
            <InputNumber min={0} className="full-width-control" />
          </Form.Item>
          <Form.Item label="Shelf Location" name="shelf_location">
            <Input />
          </Form.Item>
          <Form.Item label="Active" name="is_active" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>Save</Button>
        </Form>
      </Card>
    </div>
  );
};
