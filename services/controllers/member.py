"""HTTP controllers for society member management."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from core.exceptions.exceptions import ActiveLendingError
from core.responses.mixins import ResponseMixin
from services.factories.member import MemberFactory
from services.models.member import Member
from services.serializers.member import MemberSerializer
from services.shared.logger import logger
from services.shared.filters import MemberFilter
from services.shared.pagination import StandardPagination


class MemberListController(ResponseMixin, GenericAPIView):
    """Search, paginate, and create society members."""

    serializer_class = MemberSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MemberFilter
    search_fields = ["first_name", "last_name", "email", "membership_number", "phone"]
    ordering_fields = ["first_name", "last_name", "membership_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Member.objects.all()

    def get(self, request):
        """Return a filtered page of non-deleted members."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        return self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data,
            message="Members retrieved successfully.",
        )

    def post(self, request):
        """Validate and create a new member."""
        serializer = MemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = MemberFactory.create_member(serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=member_created member_uuid=%s user_id=%s",
            member.uuid,
            request.user.id,
        )
        return self.success_response(
            data=MemberSerializer(member).data,
            message="Member created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class MemberOptionsController(ResponseMixin, GenericAPIView):
    """Return an unpaginated active-member collection for remote dropdowns."""

    serializer_class = MemberSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "email", "membership_number"]

    def get_queryset(self):
        return Member.objects.filter(is_active=True).order_by("first_name", "last_name")

    def get(self, request):
        members = self.filter_queryset(self.get_queryset())[:50]
        return self.success_response(
            data=self.get_serializer(members, many=True).data,
            message="Member options retrieved successfully.",
        )


class MemberDetailController(ResponseMixin, APIView):
    """Retrieve, modify, or deactivate an individual member."""

    serializer_class = MemberSerializer

    def get(self, request, uuid):
        """Return one non-deleted member by UUID."""
        member = get_object_or_404(Member, uuid=uuid)
        return self.success_response(
            data=MemberSerializer(member).data, message="Member retrieved successfully."
        )

    def patch(self, request, uuid):
        """Apply a partial update to a member."""
        member = get_object_or_404(Member, uuid=uuid)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        member = MemberFactory.update_member(member, serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=member_updated member_uuid=%s user_id=%s",
            member.uuid,
            request.user.id,
        )
        return self.success_response(
            data=MemberSerializer(member).data, message="Member updated successfully."
        )

    def put(self, request, uuid):
        """Update a member using the endpoint's partial-update semantics."""
        return self.patch(request, uuid)

    def delete(self, request, uuid):
        """Soft-delete a member while retaining historical records."""
        member = get_object_or_404(Member, uuid=uuid)
        if member.lendings.filter(status__in=["BORROWED", "OVERDUE"]).exists():
            raise ActiveLendingError(
                "A member with active lendings cannot be deactivated."
            )
        member.soft_delete()
        logger.info(
            "[SOCIETY_CONNECT] event=member_deactivated member_uuid=%s user_id=%s",
            member.uuid,
            request.user.id,
        )
        return self.success_response(message="Member deactivated successfully.")
