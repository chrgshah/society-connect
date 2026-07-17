"""HTTP controllers for society member management."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.member import MemberFactory
from services.models.member import Member
from services.serializers.member import MemberSerializer
from services.shared.logger import logger


class MemberListController(ResponseMixin, APIView):
    """Search, paginate, and create society members."""

    def get(self, request):
        """Return a filtered page of non-deleted members."""
        queryset = MemberFactory.get_queryset(
            search=request.GET.get("search"), is_active=request.GET.get("is_active")
        )
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])
        serializer = MemberSerializer(items, many=True)
        total_records = queryset.count()
        return self.paginated_response(
            serializer.data,
            page,
            page_size,
            total_records,
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


class MemberDetailController(ResponseMixin, APIView):
    """Retrieve, modify, or deactivate an individual member."""

    def get(self, request, uuid):
        """Return one non-deleted member by UUID."""
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(
            data=MemberSerializer(member).data, message="Member retrieved successfully."
        )

    def patch(self, request, uuid):
        """Apply a partial update to a member."""
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
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
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
        member.soft_delete()
        logger.info(
            "[SOCIETY_CONNECT] event=member_deactivated member_uuid=%s user_id=%s",
            member.uuid,
            request.user.id,
        )
        return self.success_response(message="Member deactivated successfully.")
