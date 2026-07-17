import { Alert, Card, Descriptions, Table } from 'antd';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getMember } from '../api/memberApi';
import { getMemberBorrowedBooks } from '../api/lendingApi';
import { PageHeader } from '../components/PageHeader';
import { getErrorMessage } from '../utils/errors';
import type { Member } from '../types/member';
import type { Lending } from '../types/lending';

export const MemberDetailPage = () => {
  const { id } = useParams();
  const [member, setMember] = useState<Member | null>(null);
  const [borrowed, setBorrowed] = useState<Lending[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      try {
        const [memberResponse, borrowedResponse] = await Promise.all([getMember(id), getMemberBorrowedBooks(id)]);
        setMember(memberResponse.data.data);
        setBorrowed(borrowedResponse.data.data);
      } catch (loadError) {
        setError(getErrorMessage(loadError));
      }
    };
    void load();
  }, [id]);

  if (error) {
    return (
      <div>
        <PageHeader title="Member Details" description="View a member and their active borrowings" />
        <Alert type="error" message={error} showIcon />
      </div>
    );
  }

  if (!member) return null;

  return (
    <div>
      <PageHeader title="Member Details" description="View a member and their active borrowings" />
      <Card>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="Name">{member.first_name} {member.last_name}</Descriptions.Item>
          <Descriptions.Item label="Email">{member.email}</Descriptions.Item>
          <Descriptions.Item label="Phone">{member.phone}</Descriptions.Item>
          <Descriptions.Item label="Membership Number">{member.membership_number}</Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="Currently Borrowed Books" style={{ marginTop: 16 }}>
        <Table dataSource={borrowed} rowKey="uuid" columns={[{ title: 'Book', render: (record) => record.book.title }, { title: 'Due', dataIndex: 'due_at' }]} />
      </Card>
    </div>
  );
};
