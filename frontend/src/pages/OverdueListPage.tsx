import { Alert, Table } from 'antd';
import { useEffect, useState } from 'react';
import { getOverdueLendings } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatusTag } from '../components/StatusTag';
import { formatDateTime } from '../utils/dates';
import type { Lending } from '../types/lending';
import { getErrorMessage } from '../utils/errors';

export const OverdueListPage = () => {
  const [lendings, setLendings] = useState<Lending[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await getOverdueLendings();
        setLendings(Array.isArray(response.data.data) ? response.data.data : []);
      } catch (err) {
        setLendings([]);
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <div>
      <PageHeader title="Overdue Books" description="Books past their due date" />
      {error ? <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} /> : null}
      <Table
        loading={loading}
        dataSource={lendings}
        rowKey="uuid"
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
