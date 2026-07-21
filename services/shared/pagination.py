"""REST framework pagination defaults for list endpoints."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Provide bounded, client-configurable page sizes."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data, message="Records retrieved successfully."):
        """Return DRF pagination metadata inside the project's response envelope."""
        return Response(
            {
                "success": True,
                "message": message,
                "data": {
                    "results": data,
                    "pagination": {
                        "page": self.page.number,
                        "page_size": self.get_page_size(self.request),
                        "total_pages": self.page.paginator.num_pages or 1,
                        "total_records": self.page.paginator.count,
                        "has_next": self.page.has_next(),
                        "has_previous": self.page.has_previous(),
                    },
                },
            }
        )
