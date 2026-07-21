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
import { ROUTES } from '../config/paths';

export const AppRoutes = () => (
  <Routes>
    <Route path={ROUTES.login} element={<LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route path={ROUTES.dashboard} element={<DashboardPage />} />
        <Route path={ROUTES.members} element={<MemberListPage />} />
        <Route path={ROUTES.memberNew} element={<MemberFormPage />} />
        <Route path={ROUTES.memberDetailPattern} element={<MemberDetailPage />} />
        <Route path={ROUTES.memberEditPattern} element={<MemberFormPage />} />
        <Route path={ROUTES.books} element={<BookListPage />} />
        <Route path={ROUTES.bookNew} element={<BookFormPage />} />
        <Route path={ROUTES.bookDetailPattern} element={<BookDetailPage />} />
        <Route path={ROUTES.bookEditPattern} element={<BookFormPage />} />
        <Route path={ROUTES.borrow} element={<BorrowBookPage />} />
        <Route path={ROUTES.lendings} element={<LendingListPage />} />
        <Route path={ROUTES.overdue} element={<OverdueListPage />} />
        <Route path={ROUTES.categories} element={<CategoryListPage />} />
        <Route path={ROUTES.categoryNew} element={<CategoryFormPage />} />
        <Route path={ROUTES.categoryDetailPattern} element={<CategoryDetailPage />} />
        <Route path={ROUTES.categoryEditPattern} element={<CategoryFormPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to={ROUTES.login} replace />} />
  </Routes>
);
