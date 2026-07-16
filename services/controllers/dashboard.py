from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.dashboard import DashboardFactory
from services.serializers.dashboard import DashboardSummarySerializer


class DashboardSummaryController(ResponseMixin, APIView):
    def get(self, request):
        summary = DashboardFactory.get_summary()
        serializer = DashboardSummarySerializer(summary)
        return self.success_response(
            data=serializer.data, message="Dashboard summary retrieved successfully."
        )
