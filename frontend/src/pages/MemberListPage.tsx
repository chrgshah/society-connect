import { Alert, Button, Input, Space, Table, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateMember, getMembers } from '../api/memberApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import { useToast } from '../components/ToastProvider';
import { formatDate } from '../utils/dates';
import { getErrorMessage } from '../utils/errors';
import type { Member } from '../types/member';
import type { PaginationMeta } from '../types/api';
import { ROUTES } from '../config/paths';

export const MemberListPage = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [pagination, setPagination] = useState<Pick<PaginationMeta, 'page' | 'page_size' | 'total_records'>>({ page: 1, page_size: 20, total_records: 0 });

  const loadMembers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getMembers({ search, page: pagination.page, page_size: pagination.page_size });
      setMembers(response.data.data.results);
      setPagination((current) => ({ ...current, ...response.data.data.pagination }));
    } catch (loadError) {
      setMembers([]);
      setError(getErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadMembers(); }, [search, pagination.page, pagination.page_size]);

  const remove = (member: Member) => {
    const name = `${member.first_name} ${member.last_name}`.trim();
    confirmAction('Deactivate member', `Deactivate ${name}?`, async () => {
      try {
        await deactivateMember(member.uuid);
        toast.success(`${name} was deactivated.`, 'Member deactivated');
        await loadMembers();
      } catch (error) {
        toast.error(getErrorMessage(error), 'Member deactivation failed');
      }
    });
  };

  return (
    <div>
      <PageHeader title="Members" description="Manage library members" extra={<Button type="primary" onClick={() => navigate(ROUTES.memberNew)}>Add Member</Button>} />
      {error ? <Alert className="app-alert" type="error" message={error} showIcon /> : null}
      <Space className="list-toolbar">
        <Input.Search value={search} onChange={(e) => { setSearch(e.target.value); setPagination((p) => ({ ...p, page: 1 })); }} placeholder="Search members" />
      </Space>
      <Table
        loading={loading}
        dataSource={members}
        rowKey="uuid"
        pagination={{ current: pagination.page, pageSize: pagination.page_size, total: pagination.total_records, showSizeChanger: true, onChange: (page, pageSize) => setPagination((p) => ({ ...p, page, page_size: pageSize })) }}
        columns={[
          { title: 'Membership #', dataIndex: 'membership_number' },
          { title: 'Name', render: (record) => `${record.first_name} ${record.last_name}` },
          { title: 'Email', dataIndex: 'email' },
          { title: 'Phone', dataIndex: 'phone' },
          { title: 'Status', render: (record) => <Tag color={record.is_active ? 'green' : 'default'}>{record.is_active ? 'Active' : 'Inactive'}</Tag> },
          { title: 'Membership Date', render: (record) => formatDate(record.membership_date) },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(ROUTES.memberDetail(record.uuid))}>View</Button><Button size="small" onClick={() => navigate(ROUTES.memberEdit(record.uuid))}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
