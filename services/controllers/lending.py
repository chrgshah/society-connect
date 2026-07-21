"""HTTP controllers for borrowing, returns, and lending queries."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from core.responses.mixins import ResponseMixin
from services.factories.lending import LendingFactory
from services.models.lending import Lending
from services.models.member import Member
from services.serializers.lending import (
    BorrowBookSerializer,
    LendingSerializer,
    ReturnBookSerializer,
)
from services.shared.filters import LendingFilter
from services.shared.pagination import StandardPagination


class BorrowBookController(ResponseMixin, APIView):
    """Create a lending after validating member and book eligibility."""

    serializer_class = BorrowBookSerializer

    def post(self, request):
        """Borrow an available book for an active member."""
        serializer = BorrowBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lending = LendingFactory.borrow_book(
            member_uuid=serializer.validated_data["member_uuid"],
            book_uuid=serializer.validated_data["book_uuid"],
            due_at=serializer.validated_data.get("due_at"),
            notes=serializer.validated_data.get("notes", ""),
        )
        return self.success_response(
            data=LendingSerializer(lending).data,
            message="Book borrowed successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ReturnBookController(ResponseMixin, APIView):
    """Mark an active lending as returned."""

    serializer_class = ReturnBookSerializer

    def post(self, request, uuid):
        """Return the book associated with the lending UUID."""
        lending = get_object_or_404(Lending, uuid=uuid, deleted_at__isnull=True)
        lending = LendingFactory.return_book(lending.uuid)
        return self.success_response(
            data=LendingSerializer(lending).data, message="Book returned successfully."
        )


class LendingListController(ResponseMixin, GenericAPIView):
    """Search and paginate lending history."""

    serializer_class = LendingSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LendingFilter
    search_fields = ["notes", "member__first_name", "member__last_name", "book__title"]
    ordering_fields = ["borrowed_at", "due_at", "returned_at", "status"]
    ordering = ["-borrowed_at"]

    def get_queryset(self):
        return Lending.objects.filter(deleted_at__isnull=True).select_related(
            "member", "book"
        )

    def get(self, request):
        """Return a filtered page of lending records."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        return self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data,
            message="Lending records retrieved successfully.",
        )


class LendingDetailController(ResponseMixin, APIView):
    """Retrieve an individual lending record."""

    serializer_class = LendingSerializer

    def get(self, request, uuid):
        """Return one non-deleted lending by UUID."""
        lending = get_object_or_404(Lending, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(
            data=LendingSerializer(lending).data,
            message="Lending retrieved successfully.",
        )


class MemberBorrowedBooksController(ResponseMixin, APIView):
    """List books currently borrowed by a member."""

    serializer_class = LendingSerializer

    def get(self, request, member_uuid):
        """Return active borrowings for the specified member."""
        member = get_object_or_404(Member, uuid=member_uuid, deleted_at__isnull=True)
        lendings = LendingFactory.get_member_borrowed_books(member.uuid)
        return self.success_response(
            data=LendingSerializer(lendings, many=True).data,
            message="Borrowed books retrieved successfully.",
        )


class OverdueListController(ResponseMixin, GenericAPIView):
    """List lending records whose due date has passed."""

    serializer_class = LendingSerializer
    pagination_class = StandardPagination

    def get(self, request):
        """Return all borrowed or overdue records past their due date."""
        overdue = LendingFactory.get_overdue_records()
        if "page" in request.query_params or "page_size" in request.query_params:
            page = self.paginate_queryset(overdue)
            return self.paginator.get_paginated_response(
                self.get_serializer(page, many=True).data,
                message="Overdue records retrieved successfully.",
            )
        return self.success_response(
            data=LendingSerializer(overdue, many=True).data,
            message="Overdue records retrieved successfully.",
        )
