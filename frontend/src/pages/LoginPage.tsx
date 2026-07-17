import { Alert, Button, Card, Form, Input, Typography } from 'antd';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { getErrorMessage } from '../utils/errors';

export const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    setError('');
    try {
      await login(values.username, values.password);
      navigate('/');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: '80px auto' }}>
      <Card>
        <Typography.Title level={2}>Society Connect Login</Typography.Title>
        {error ? <Alert type="error" message={error} style={{ marginBottom: 16 }} /> : null}
        <Form onFinish={onFinish} layout="vertical" onValuesChange={() => setError('')}>
          <Form.Item label="Username" name="username" rules={[{ required: true, whitespace: true, message: 'Please enter Username' }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true, message: 'Please enter Password' }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Log in
          </Button>
        </Form>
      </Card>
    </div>
  );
};
