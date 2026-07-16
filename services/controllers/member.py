from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.member import MemberFactory
from services.models.member import Member
from services.serializers.member import MemberSerializer


class MemberListController(ResponseMixin, APIView):
    def get(self, request):
        queryset = MemberFactory.get_queryset(search=request.GET.get("search"), is_active=request.GET.get("is_active"))
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])
        serializer = MemberSerializer(items, many=True)
        total_records = queryset.count()
        return self.paginated_response(serializer.data, page, page_size, total_records, message="Members retrieved successfully.")

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = MemberFactory.create_member(serializer.validated_data)
        return self.success_response(data=MemberSerializer(member).data, message="Member created successfully.", status_code=status.HTTP_201_CREATED)


class MemberDetailController(ResponseMixin, APIView):
    def get(self, request, uuid):
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(data=MemberSerializer(member).data, message="Member retrieved successfully.")

    def patch(self, request, uuid):
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        member = MemberFactory.update_member(member, serializer.validated_data)
        return self.success_response(data=MemberSerializer(member).data, message="Member updated successfully.")

    def put(self, request, uuid):
        return self.patch(request, uuid)

    def delete(self, request, uuid):
        member = get_object_or_404(Member, uuid=uuid, deleted_at__isnull=True)
        member.soft_delete()
        return self.success_response(message="Member deactivated successfully.")
