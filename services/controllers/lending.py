from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.lending import LendingFactory
from services.models.lending import Lending
from services.models.member import Member
from services.serializers.lending import (
    BorrowBookSerializer,
    LendingSerializer,
)


class BorrowBookController(ResponseMixin, APIView):
    def post(self, request):
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
    def post(self, request, uuid):
        lending = get_object_or_404(Lending, uuid=uuid, deleted_at__isnull=True)
        lending = LendingFactory.return_book(lending.uuid)
        return self.success_response(
            data=LendingSerializer(lending).data, message="Book returned successfully."
        )


class LendingListController(ResponseMixin, APIView):
    def get(self, request):
        queryset = LendingFactory.get_queryset(
            search=request.GET.get("search"),
            status=request.GET.get("status"),
            member_uuid=request.GET.get("member_uuid"),
            book_uuid=request.GET.get("book_uuid"),
            from_date=request.GET.get("from_date"),
            to_date=request.GET.get("to_date"),
        )
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])
        serializer = LendingSerializer(items, many=True)
        return self.paginated_response(
            serializer.data,
            page,
            page_size,
            queryset.count(),
            message="Lending records retrieved successfully.",
        )


class LendingDetailController(ResponseMixin, APIView):
    def get(self, request, uuid):
        lending = get_object_or_404(Lending, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(
            data=LendingSerializer(lending).data,
            message="Lending retrieved successfully.",
        )


class MemberBorrowedBooksController(ResponseMixin, APIView):
    def get(self, request, member_uuid):
        member = get_object_or_404(Member, uuid=member_uuid, deleted_at__isnull=True)
        lendings = LendingFactory.get_member_borrowed_books(member.uuid)
        return self.success_response(
            data=LendingSerializer(lendings, many=True).data,
            message="Borrowed books retrieved successfully.",
        )


class OverdueListController(ResponseMixin, APIView):
    def get(self, request):
        overdue = LendingFactory.get_overdue_records()
        return self.success_response(
            data=LendingSerializer(overdue, many=True).data,
            message="Overdue records retrieved successfully.",
        )
