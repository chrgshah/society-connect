"""HTTP controller for dashboard aggregate statistics."""

from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.dashboard import DashboardFactory
from services.serializers.dashboard import (
    DashboardDateRangeSerializer,
    DashboardSummarySerializer,
)


class DashboardSummaryController(ResponseMixin, APIView):
    """Return the high-level library and membership summary."""

    def get(self, request):
        """Calculate, serialize, and return dashboard counters."""
        query = DashboardDateRangeSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        summary = DashboardFactory.get_summary(**query.validated_data)
        serializer = DashboardSummarySerializer(summary)
        return self.success_response(
            data=serializer.data, message="Dashboard summary retrieved successfully."
        )

    serializer_class = DashboardSummarySerializer
