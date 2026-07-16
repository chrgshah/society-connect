import { Button, Input, Select, Space, Table, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deactivateMember, getMembers } from '../api/memberApi';
import { PageHeader } from '../components/PageHeader';
import { confirmAction } from '../components/ConfirmAction';
import { formatDate } from '../utils/dates';
import type { Member } from '../types/member';

export const MemberListPage = () => {
  const navigate = useNavigate();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  const loadMembers = async () => {
    setLoading(true);
    try {
      const response = await getMembers({ search, page: 1, page_size: 20 });
      setMembers(response.data.data.results);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void loadMembers(); }, [search]);

  const remove = (member: Member) => {
    const name = `${member.first_name} ${member.last_name}`.trim();
    confirmAction('Deactivate member', `Deactivate ${name}?`, async () => {
      await deactivateMember(member.uuid);
      void loadMembers();
    });
  };

  return (
    <div>
      <PageHeader title="Members" description="Manage library members" extra={<Button type="primary" onClick={() => navigate('/members/new')}>Add Member</Button>} />
      <Space style={{ marginBottom: 16 }}>
        <Input.Search value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search members" />
      </Space>
      <Table
        loading={loading}
        dataSource={members}
        rowKey="uuid"
        columns={[
          { title: 'Membership #', dataIndex: 'membership_number' },
          { title: 'Name', render: (record) => `${record.first_name} ${record.last_name}` },
          { title: 'Email', dataIndex: 'email' },
          { title: 'Phone', dataIndex: 'phone' },
          { title: 'Status', render: (record) => <Tag color={record.is_active ? 'green' : 'default'}>{record.is_active ? 'Active' : 'Inactive'}</Tag> },
          { title: 'Membership Date', render: (record) => formatDate(record.membership_date) },
          { title: 'Actions', render: (record) => <Space><Button size="small" onClick={() => navigate(`/members/${record.uuid}`)}>View</Button><Button size="small" onClick={() => navigate(`/members/${record.uuid}/edit`)}>Edit</Button><Button size="small" danger onClick={() => remove(record)}>Deactivate</Button></Space> },
        ]}
      />
    </div>
  );
};
