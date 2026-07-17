"""Convert application and DRF exceptions into the common API envelope."""

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from services.shared.logger import logger

from .exceptions import ApiError


def exception_handler(exc, context):
    """Return a consistent error response and log failures by severity."""
    response = drf_exception_handler(exc, context)
    view_name = (
        context.get("view").__class__.__name__ if context.get("view") else "unknown"
    )
    if isinstance(exc, ApiError):
        logger.warning(
            "[SOCIETY_CONNECT] event=api_error exception=%s status_code=%s view=%s",
            type(exc).__name__,
            exc.status_code,
            view_name,
        )
        return Response(
            {"success": False, "message": exc.message, "errors": exc.errors},
            status=exc.status_code,
        )
    if response is not None:
        logger.warning(
            "[SOCIETY_CONNECT] event=request_failed exception=%s "
            "status_code=%s view=%s",
            type(exc).__name__,
            response.status_code,
            view_name,
        )
        data = response.data
        if isinstance(data, dict):
            message = data.get("detail") or "Request failed."
            return Response(
                {"success": False, "message": message, "errors": data},
                status=response.status_code,
            )
    logger.exception(
        "[SOCIETY_CONNECT] event=unhandled_api_exception exception=%s view=%s",
        type(exc).__name__,
        view_name,
    )
    return response
