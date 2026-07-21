import { Alert, Button, Card, DatePicker, Form, Input, Select, Spin } from 'antd';
import type { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import { borrowBook } from '../api/lendingApi';
import { getMemberOptions } from '../api/memberApi';
import { getBookOptions } from '../api/bookApi';
import { PageHeader } from '../components/PageHeader';
import { useToast } from '../components/ToastProvider';
import { getErrorMessage } from '../utils/errors';
import type { Member } from '../types/member';
import type { Book } from '../types/book';
import { useDebouncedValue } from '../hooks/useDebouncedValue';

interface BorrowBookFormValues {
  member_uuid: string;
  book_uuid: string;
  due_at?: Dayjs;
  notes?: string;
}

export const BorrowBookPage = () => {
  const [form] = Form.useForm<BorrowBookFormValues>();
  const toast = useToast();
  const [members, setMembers] = useState<Member[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [memberSearch, setMemberSearch] = useState('');
  const [bookSearch, setBookSearch] = useState('');
  const [membersLoading, setMembersLoading] = useState(false);
  const [booksLoading, setBooksLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const debouncedMemberSearch = useDebouncedValue(memberSearch);
  const debouncedBookSearch = useDebouncedValue(bookSearch);

  useEffect(() => {
    const search = debouncedMemberSearch.trim();
    if (!search) {
      setMembers([]);
      setMembersLoading(false);
      return;
    }

    let cancelled = false;
    const load = async () => {
      setMembersLoading(true);
      try {
        const response = await getMemberOptions(search);
        if (!cancelled) {
          setMembers(response.data.data);
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
    };
    void load();

    return () => {
      cancelled = true;
    };
  }, [debouncedMemberSearch]);

  useEffect(() => {
    const search = debouncedBookSearch.trim();
    if (!search) {
      setBooks([]);
      setBooksLoading(false);
      return;
    }
    let cancelled = false;
    const load = async () => {
      setBooksLoading(true);
      try {
        const response = await getBookOptions(search);
        if (!cancelled) setBooks(response.data.data);
      } catch (loadError) {
        if (!cancelled) {
          setBooks([]);
          setError(getErrorMessage(loadError));
        }
      } finally {
        if (!cancelled) setBooksLoading(false);
      }
    };
    void load();
    return () => { cancelled = true; };
  }, [debouncedBookSearch]);

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
      toast.success('The borrowing record was created.', 'Book borrowed');
      form.resetFields();
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      toast.error(message, 'Borrowing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Borrow Book" description="Create a new borrowing record" />
      <Card>
        {message ? <Alert type="success" message={message} className="app-alert" /> : null}
        {error ? <Alert type="error" message={error} className="app-alert" /> : null}
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
            <Select
              showSearch
              filterOption={false}
              onSearch={setBookSearch}
              placeholder="Type a book title, ISBN, or author"
              notFoundContent={booksLoading ? <Spin size="small" /> : bookSearch.trim() ? 'No books found' : 'Start typing to search'}
              options={books.map((book) => ({ label: `${book.title} (${book.author})`, value: book.uuid }))}
            />
          </Form.Item>
          <Form.Item label="Due Date" name="due_at">
            <DatePicker showTime className="full-width-control" />
          </Form.Item>
          <Form.Item label="Notes" name="notes" rules={[{ max: 2500, message: 'Notes cannot exceed 2,500 characters' }]}>
            <Input.TextArea maxLength={2500} showCount />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>Borrow</Button>
        </Form>
      </Card>
    </div>
  );
};
