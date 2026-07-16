import dayjs from 'dayjs';

export const formatDate = (value?: string) => (value ? dayjs(value).format('YYYY-MM-DD') : '-');
export const formatDateTime = (value?: string) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-');
