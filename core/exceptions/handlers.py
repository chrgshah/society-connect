from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .exceptions import ApiError


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if isinstance(exc, ApiError):
        return Response(
            {"success": False, "message": exc.message, "errors": exc.errors},
            status=exc.status_code,
        )
    if response is not None:
        data = response.data
        if isinstance(data, dict):
            message = data.get("detail") or "Request failed."
            return Response(
                {"success": False, "message": message, "errors": data},
                status=response.status_code,
            )
    return response
