"""Serialization schemas used by service controllers."""

from .authentication import (
    LoginSerializer as LoginSerializer,
    LogoutSerializer as LogoutSerializer,
    RefreshSerializer as RefreshSerializer,
)
from .book import BookSerializer as BookSerializer
from .book import BookCategorySerializer as BookCategorySerializer
from .category import CategorySerializer as CategorySerializer
from .dashboard import DashboardSummarySerializer as DashboardSummarySerializer
from .lending import BorrowBookSerializer as BorrowBookSerializer
from .lending import LendingSerializer as LendingSerializer
from .lending import ReturnBookSerializer as ReturnBookSerializer
from .member import MemberSerializer as MemberSerializer
