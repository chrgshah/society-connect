import { Table } from 'antd';
import type { TableProps } from 'antd';

interface DataTableProps<T> extends TableProps<T> {
  loading?: boolean;
}

export const DataTable = <T extends object>({ loading, ...props }: DataTableProps<T>) => (
  <Table
    loading={loading}
    pagination={{ pageSize: 10, showSizeChanger: true }}
    locale={{ emptyText: 'No records found' }}
    {...props}
  />
);
