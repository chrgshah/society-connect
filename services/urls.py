from django.http import HttpResponse
from django.urls import path

from .controllers.authentication import AuthCsrfController, AuthLoginController, AuthMeController, AuthRefreshController, AuthLogoutController
from .controllers.dashboard import DashboardSummaryController
from .controllers.lending import BorrowBookController, LendingDetailController, LendingListController, MemberBorrowedBooksController, OverdueListController, ReturnBookController
from .controllers.member import MemberDetailController, MemberListController
from .controllers.book import BookDetailController, BookListController

urlpatterns = [
    path("health/", lambda request: HttpResponse("ok")),
    path("auth/csrf/", AuthCsrfController.as_view(), name="auth-csrf"),
    path("auth/login/", AuthLoginController.as_view(), name="auth-login"),
    path("auth/refresh/", AuthRefreshController.as_view(), name="auth-refresh"),
    path("auth/logout/", AuthLogoutController.as_view(), name="auth-logout"),
    path("auth/me/", AuthMeController.as_view(), name="auth-me"),
    path("members/", MemberListController.as_view(), name="member-list"),
    path("members/<uuid:uuid>/", MemberDetailController.as_view(), name="member-detail"),
    path("books/", BookListController.as_view(), name="book-list"),
    path("books/<uuid:uuid>/", BookDetailController.as_view(), name="book-detail"),
    path("lending/borrow/", BorrowBookController.as_view(), name="borrow-book"),
    path("lending/", LendingListController.as_view(), name="lending-list"),
    path("lending/<uuid:uuid>/return/", ReturnBookController.as_view(), name="return-book"),
    path("lending/<uuid:uuid>/", LendingDetailController.as_view(), name="lending-detail"),
    path("members/<uuid:member_uuid>/borrowed-books/", MemberBorrowedBooksController.as_view(), name="borrowed-books"),
    path("lending/overdue/", OverdueListController.as_view(), name="overdue-list"),
    path("dashboard/summary/", DashboardSummaryController.as_view(), name="dashboard-summary"),
]
