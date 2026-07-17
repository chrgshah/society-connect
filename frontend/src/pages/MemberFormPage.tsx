import { Alert, Button, Card, DatePicker, Form, Input, Switch } from 'antd';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { createMember, getMember, updateMember } from '../api/memberApi';
import { PageHeader } from '../components/PageHeader';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';

interface MemberFormValues {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address?: string;
  membership_number: string;
  membership_date: Dayjs;
  is_active: boolean;
}

export const MemberFormPage = () => {
  const [form] = Form.useForm<MemberFormValues>();
  const navigate = useNavigate();
  const toast = useToast();
  const { id } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      if (!id || id === 'new') return;
      try {
        const response = await getMember(id);
        const member = response.data.data;
        form.setFieldsValue({ ...member, membership_date: dayjs(member.membership_date) });
      } catch (loadError) {
        setError(getErrorMessage(loadError));
      }
    };
    void load();
  }, [id, form]);

  const onFinish = async (values: MemberFormValues) => {
    setLoading(true);
    setError('');
    try {
      const payload = {
        ...values,
        first_name: values.first_name.trim(),
        last_name: values.last_name.trim(),
        email: values.email.trim().toLowerCase(),
        phone: values.phone.trim(),
        address: values.address?.trim() || '',
        membership_number: values.membership_number.trim(),
        membership_date: values.membership_date.format('YYYY-MM-DD'),
      };
      if (id && id !== 'new') {
        await updateMember(id, payload);
        toast.success('The member details were updated.', 'Member updated');
      } else {
        await createMember(payload);
        toast.success('The new member was added.', 'Member added');
      }
      navigate('/members');
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      toast.error(message, id && id !== 'new' ? 'Member update failed' : 'Member creation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title={id && id !== 'new' ? 'Edit Member' : 'Create Member'} description="Add or edit a library member" />
      <Card>
        {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} /> : null}
        <Form
          form={form}
          layout="vertical"
          initialValues={{ is_active: true }}
          onFinish={onFinish}
          onValuesChange={() => {
            if (error) setError('');
          }}
        >
          <Form.Item label="First Name" name="first_name" rules={[{ required: true, whitespace: true, message: 'Please enter First Name' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Last Name" name="last_name" rules={[{ required: true, whitespace: true, message: 'Please enter Last Name' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="email" rules={[{ required: true, message: 'Please enter Email' }, { type: 'email', message: 'Please enter a valid Email' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Phone" name="phone" rules={[{ required: true, whitespace: true, message: 'Please enter Phone' }]}>
            <Input inputMode="tel" />
          </Form.Item>
          <Form.Item label="Address" name="address">
            <Input />
          </Form.Item>
          <Form.Item label="Membership Number" name="membership_number" rules={[{ required: true, whitespace: true, message: 'Please enter Membership Number' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Membership Date" name="membership_date" rules={[{ required: true, message: 'Please enter Membership Date' }]}>
            <DatePicker style={{ width: '100%' }} />
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
