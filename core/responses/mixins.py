"""Response-building mixin shared by API controllers."""

from rest_framework import status
from rest_framework.response import Response


class ResponseMixin:
    """Build success, error, and paginated responses with one schema."""

    def success_response(
        self, data=None, message="Success.", status_code=status.HTTP_200_OK
    ):
        """Return a successful response containing optional serialized data."""
        return Response(
            {
                "success": True,
                "message": message,
                "data": {} if data is None else data,
            },
            status=status_code,
        )

    def error_response(
        self,
        message="Request failed.",
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        """Return a structured client error response."""
        return Response(
            {"success": False, "message": message, "errors": errors or {}},
            status=status_code,
        )
