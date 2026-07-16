import { Card, Col, Row, Table, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { getDashboardSummary } from '../api/dashboardApi';
import { getLendings } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { StatusTag } from '../components/StatusTag';
import { formatDateTime } from '../utils/dates';

export const DashboardPage = () => {
  const [summary, setSummary] = useState<Record<string, number>>({});
  const [lendings, setLendings] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      const [summaryResponse, lendingsResponse] = await Promise.all([getDashboardSummary(), getLendings({ page: 1, page_size: 5 })]);
      setSummary(summaryResponse.data.data);
      setLendings(lendingsResponse.data.data.results);
    };
    void load();
  }, []);

  return (
    <div>
      <PageHeader title="Dashboard" description="At-a-glance library statistics" />
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8}><StatCard title="Total Books" value={summary.total_books ?? 0} /></Col>
        <Col xs={24} sm={12} md={8}><StatCard title="Available Copies" value={summary.available_copies ?? 0} /></Col>
        <Col xs={24} sm={12} md={8}><StatCard title="Borrowed Copies" value={summary.borrowed_copies ?? 0} /></Col>
        <Col xs={24} sm={12} md={8}><StatCard title="Total Members" value={summary.total_members ?? 0} /></Col>
        <Col xs={24} sm={12} md={8}><StatCard title="Active Members" value={summary.active_members ?? 0} /></Col>
        <Col xs={24} sm={12} md={8}><StatCard title="Overdue" value={summary.overdue_borrowings ?? 0} /></Col>
      </Row>
      <Card title="Recent Lending Records" style={{ marginTop: 24 }}>
        <Table
          dataSource={lendings}
          rowKey="uuid"
          columns={[
            { title: 'Member', dataIndex: ['member', 'full_name'] },
            { title: 'Book', dataIndex: ['book', 'title'] },
            { title: 'Due', render: (record) => formatDateTime(record.due_at) },
            { title: 'Status', render: (record) => <StatusTag value={record.status} /> },
          ]}
        />
      </Card>
    </div>
  );
};
