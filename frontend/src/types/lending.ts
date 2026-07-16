export interface Lending {
  uuid: string;
  member: {
    uuid: string;
    full_name: string;
  };
  book: {
    uuid: string;
    title: string;
  };
  borrowed_at: string;
  due_at: string;
  returned_at?: string;
  status: string;
  notes: string;
}
