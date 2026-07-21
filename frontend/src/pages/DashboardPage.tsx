import { Alert, Card, Col, DatePicker, Row, Table } from 'antd';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import { useEffect, useState } from 'react';
import { getDashboardSummary } from '../api/dashboardApi';
import { getLendings } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { StatusTag } from '../components/StatusTag';
import { formatDateTime } from '../utils/dates';
import { getErrorMessage } from '../utils/errors';
import type { Lending } from '../types/lending';

const { RangePicker } = DatePicker;
type DateRange = [Dayjs, Dayjs];

export const DashboardPage = () => {
  const [summary, setSummary] = useState<Record<string, number>>({});
  const [lendings, setLendings] = useState<Lending[]>([]);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState<DateRange>([
    dayjs().subtract(6, 'day').startOf('day'),
    dayjs().startOf('day'),
  ]);

  useEffect(() => {
    const load = async () => {
      try {
        setError('');
        const params = {
          from_date: dateRange[0].format('YYYY-MM-DD'),
          to_date: dateRange[1].format('YYYY-MM-DD'),
        };
        const [summaryResponse, lendingsResponse] = await Promise.all([
          getDashboardSummary(params),
          getLendings({ ...params, page: 1, page_size: 5 }),
        ]);
        setSummary(summaryResponse.data.data);
        setLendings(lendingsResponse.data.data.results);
      } catch (loadError) {
        setError(getErrorMessage(loadError));
      }
    };
    void load();
  }, [dateRange]);

  const changeDateRange = (dates: null | [Dayjs | null, Dayjs | null]) => {
    if (!dates?.[0] || !dates[1]) return;
    if (dates[1].isAfter(dates[0].add(6, 'month'), 'day')) {
      setError('Date range cannot exceed six months.');
      return;
    }
    setDateRange([dates[0].startOf('day'), dates[1].startOf('day')]);
  };

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="At-a-glance library statistics"
        extra={(
          <RangePicker
            allowClear={false}
            value={dateRange}
            onChange={changeDateRange}
            disabledDate={(current) => current.isAfter(dayjs(), 'day')}
          />
        )}
      />
      {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} /> : null}
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
          pagination={false}
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
