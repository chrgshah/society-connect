import { Card, Statistic } from 'antd';

interface StatCardProps {
  title: string;
  value: number | string;
}

export const StatCard = ({ title, value }: StatCardProps) => (
  <Card>
    <Statistic title={title} value={value} />
  </Card>
);
