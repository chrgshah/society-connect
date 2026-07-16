import { Space, Typography } from 'antd';

interface PageHeaderProps {
  title: string;
  description?: string;
  extra?: React.ReactNode;
}

export const PageHeader = ({ title, description, extra }: PageHeaderProps) => (
  <div style={{ marginBottom: 24 }}>
    <Space direction="vertical" size="small">
      <Typography.Title level={3} style={{ margin: 0 }}>
        {title}
      </Typography.Title>
      {description ? <Typography.Text type="secondary">{description}</Typography.Text> : null}
    </Space>
    {extra ? <div style={{ marginTop: 16 }}>{extra}</div> : null}
  </div>
);
