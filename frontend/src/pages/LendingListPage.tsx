import { Alert, Button, Table } from 'antd';
import { useEffect, useState } from 'react';
import { getLendings, returnBook } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatusTag } from '../components/StatusTag';
import { confirmAction } from '../components/ConfirmAction';
import { useToast } from '../components/ToastProvider';
import { formatDateTime } from '../utils/dates';
import { getErrorMessage } from '../utils/errors';
import type { Lending } from '../types/lending';
import type { PaginationMeta } from '../types/api';

export const LendingListPage = () => {
  const toast = useToast();
  const [lendings, setLendings] = useState<Lending[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState<Pick<PaginationMeta, 'page' | 'page_size' | 'total_records'>>({ page: 1, page_size: 20, total_records: 0 });

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getLendings({ page: pagination.page, page_size: pagination.page_size });
      setLendings(response.data.data.results);
      setPagination((current) => ({ ...current, ...response.data.data.pagination }));
    } catch (loadError) {
      setLendings([]);
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [pagination.page, pagination.page_size]);

  const handleReturn = (record: Lending) => {
    confirmAction('Return book', 'Return this borrowed book?', async () => {
      try {
        await returnBook(record.uuid);
        toast.success('The book was returned successfully.', 'Book returned');
        await load();
      } catch (error) {
        toast.error(getErrorMessage(error), 'Book return failed');
      }
    });
  };

  return (
    <div>
      <PageHeader title="Lending Records" description="Track borrowings and returns" />
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
          { title: 'Returned', render: (record) => formatDateTime(record.returned_at) },
          { title: 'Status', render: (record) => <StatusTag value={record.status} /> },
          { title: 'Actions', render: (record) => record.status !== 'RETURNED' ? <Button size="small" onClick={() => handleReturn(record)}>Return</Button> : null },
        ]}
      />
    </div>
  );
};
