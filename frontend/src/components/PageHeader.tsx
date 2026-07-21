import { Space, Typography } from 'antd';

interface PageHeaderProps {
  title: string;
  description?: string;
  extra?: React.ReactNode;
}

export const PageHeader = ({ title, description, extra }: PageHeaderProps) => (
  <div className="page-header">
    <Space direction="vertical" size="small">
      <Typography.Title level={3} className="page-header-title">
        {title}
      </Typography.Title>
      {description ? <Typography.Text type="secondary">{description}</Typography.Text> : null}
    </Space>
    {extra ? <div className="page-header-extra">{extra}</div> : null}
  </div>
);
