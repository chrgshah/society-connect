import { Alert, Table } from 'antd';
import { useEffect, useState } from 'react';
import { getOverdueLendings } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatusTag } from '../components/StatusTag';
import { formatDateTime } from '../utils/dates';
import type { Lending } from '../types/lending';
import { getErrorMessage } from '../utils/errors';
import type { PaginationMeta } from '../types/api';

export const OverdueListPage = () => {
  const [lendings, setLendings] = useState<Lending[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState<Pick<PaginationMeta, 'page' | 'page_size' | 'total_records'>>({ page: 1, page_size: 20, total_records: 0 });

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await getOverdueLendings({ page: pagination.page, page_size: pagination.page_size });
        setLendings(response.data.data.results);
        setPagination((current) => ({ ...current, ...response.data.data.pagination }));
      } catch (err) {
        setLendings([]);
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [pagination.page, pagination.page_size]);

  return (
    <div>
      <PageHeader title="Overdue Books" description="Books past their due date" />
      {error ? <Alert className="app-alert" type="error" message={error} showIcon /> : null}
      <Table
        loading={loading}
        dataSource={lendings}
        rowKey="uuid"
        pagination={{ current: pagination.page, pageSize: pagination.page_size, total: pagination.total_records, showSizeChanger: true, onChange: (page, pageSize) => setPagination((p) => ({ ...p, page, page_size: pageSize })) }}
        columns={[
          { title: 'Member', render: (record) => record.member.full_name },
          { title: 'Book', render: (record) => record.book.title },
          { title: 'Borrowed', render: (record) => formatDateTime(record.borrowed_at) },
          { title: 'Due', render: (record) => formatDateTime(record.due_at) },
          { title: 'Status', render: (record) => <StatusTag value={record.status} /> },
        ]}
      />
    </div>
  );
};
