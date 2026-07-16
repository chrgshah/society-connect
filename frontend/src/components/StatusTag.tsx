import { Tag } from 'antd';

const statusMap: Record<string, string> = {
  ACTIVE: 'green',
  INACTIVE: 'default',
  AVAILABLE: 'green',
  UNAVAILABLE: 'red',
  BORROWED: 'blue',
  RETURNED: 'green',
  OVERDUE: 'red',
};

export const StatusTag = ({ value }: { value?: string }) => {
  if (!value) return null;
  const color = statusMap[value.toUpperCase()] || 'default';
  return <Tag color={color}>{value}</Tag>;
};
