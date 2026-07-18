import { Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { AppLayout } from '../components/AppLayout';
import { BookDetailPage } from '../pages/BookDetailPage';
import { BookFormPage } from '../pages/BookFormPage';
import { BookListPage } from '../pages/BookListPage';
import { BorrowBookPage } from '../pages/BorrowBookPage';
import { DashboardPage } from '../pages/DashboardPage';
import { LendingListPage } from '../pages/LendingListPage';
import { LoginPage } from '../pages/LoginPage';
import { MemberDetailPage } from '../pages/MemberDetailPage';
import { MemberFormPage } from '../pages/MemberFormPage';
import { MemberListPage } from '../pages/MemberListPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { OverdueListPage } from '../pages/OverdueListPage';
import { CategoryListPage } from '../pages/CategoryListPage';
import { CategoryDetailPage } from '../pages/CategoryDetailPage';
import { CategoryFormPage } from '../pages/CategoryFormPage';

export const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/members" element={<MemberListPage />} />
        <Route path="/members/new" element={<MemberFormPage />} />
        <Route path="/members/:id" element={<MemberDetailPage />} />
        <Route path="/members/:id/edit" element={<MemberFormPage />} />
        <Route path="/books" element={<BookListPage />} />
        <Route path="/books/new" element={<BookFormPage />} />
        <Route path="/books/:id" element={<BookDetailPage />} />
        <Route path="/books/:id/edit" element={<BookFormPage />} />
        <Route path="/borrow" element={<BorrowBookPage />} />
        <Route path="/lendings" element={<LendingListPage />} />
        <Route path="/overdue" element={<OverdueListPage />} />
        <Route path="/categories" element={<CategoryListPage />} />
        <Route path="/categories/new" element={<CategoryFormPage />} />
        <Route path="/categories/:id" element={<CategoryDetailPage />} />
        <Route path="/categories/:id/edit" element={<CategoryFormPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes>
);
