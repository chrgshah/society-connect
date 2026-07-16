import { Alert, Button, Card, DatePicker, Form, Input, Select, Spin } from 'antd';
import type { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import { borrowBook } from '../api/lendingApi';
import { getMembers } from '../api/memberApi';
import { getBooks } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import { getErrorMessage } from '../utils/errors';
import type { Member } from '../types/member';
import type { Book } from '../types/book';

interface BorrowBookFormValues {
  member_uuid: string;
  book_uuid: string;
  due_at?: Dayjs;
  notes?: string;
}

export const BorrowBookPage = () => {
  const [form] = Form.useForm<BorrowBookFormValues>();
  const [members, setMembers] = useState<Member[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [memberSearch, setMemberSearch] = useState('');
  const [membersLoading, setMembersLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const loadBooks = async () => {
      const booksResponse = await getBooks({ is_available: true, page: 1, page_size: 50 });
      setBooks(booksResponse.data.data.results);
    };
    void loadBooks();
  }, []);

  useEffect(() => {
    const search = memberSearch.trim();
    if (!search) {
      setMembers([]);
      setMembersLoading(false);
      return;
    }

    let cancelled = false;
    const timer = window.setTimeout(async () => {
      setMembersLoading(true);
      try {
        const response = await getMembers({
          search,
          is_active: true,
          page: 1,
          page_size: 20,
        });
        if (!cancelled) {
          setMembers(response.data.data.results);
        }
      } catch (err) {
        if (!cancelled) {
          setMembers([]);
          setError(getErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setMembersLoading(false);
        }
      }
    }, 400);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [memberSearch]);

  const onFinish = async (values: BorrowBookFormValues) => {
    setLoading(true);
    setError('');
    setMessage('');
    try {
      await borrowBook({
        member_uuid: values.member_uuid,
        book_uuid: values.book_uuid,
        due_at: values.due_at?.toISOString(),
        notes: values.notes?.trim() || '',
      });
      setMessage('Book borrowed successfully.');
      form.resetFields();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Borrow Book" description="Create a new borrowing record" />
      <Card>
        {message ? <Alert type="success" message={message} style={{ marginBottom: 16 }} /> : null}
        {error ? <Alert type="error" message={error} style={{ marginBottom: 16 }} /> : null}
        <Form form={form} layout="vertical" onFinish={onFinish} onValuesChange={() => { setError(''); setMessage(''); }}>
          <Form.Item label="Member" name="member_uuid" rules={[{ required: true, message: 'Please select a Member' }]}>
            <Select
              showSearch
              filterOption={false}
              onSearch={setMemberSearch}
              placeholder="Type a member name or email"
              notFoundContent={membersLoading ? <Spin size="small" /> : memberSearch.trim() ? 'No members found' : 'Start typing to search'}
              options={members.map((member) => ({
                label: `${member.first_name} ${member.last_name} (${member.email})`,
                value: member.uuid,
              }))}
            />
          </Form.Item>
          <Form.Item label="Book" name="book_uuid" rules={[{ required: true, message: 'Please select a Book' }]}>
            <Select showSearch optionFilterProp="label" placeholder="Select a book" options={books.map((book) => ({ label: book.title, value: book.uuid }))} />
          </Form.Item>
          <Form.Item label="Due Date" name="due_at">
            <DatePicker showTime style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="Notes" name="notes">
            <Input.TextArea />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>Borrow</Button>
        </Form>
      </Card>
    </div>
  );
};
