import { Button, Table } from 'antd';
import { useEffect, useState } from 'react';
import { getLendings, returnBook } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { StatusTag } from '../components/StatusTag';
import { confirmAction } from '../components/ConfirmAction';
import { formatDateTime } from '../utils/dates';
import type { Lending } from '../types/lending';

export const LendingListPage = () => {
  const [lendings, setLendings] = useState<Lending[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const response = await getLendings({ page: 1, page_size: 20 });
      setLendings(response.data.data.results);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const handleReturn = (record: Lending) => {
    confirmAction('Return book', 'Return this borrowed book?', async () => {
      await returnBook(record.uuid);
      void load();
    });
  };

  return (
    <div>
      <PageHeader title="Lending Records" description="Track borrowings and returns" />
      <Table
        loading={loading}
        dataSource={lendings}
        rowKey="uuid"
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
