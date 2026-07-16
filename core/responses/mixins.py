from rest_framework import status
from rest_framework.response import Response


class ResponseMixin:
    def success_response(
        self, data=None, message="Success.", status_code=status.HTTP_200_OK
    ):
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
        return Response(
            {"success": False, "message": message, "errors": errors or {}},
            status=status_code,
        )

    def paginated_response(
        self,
        results,
        page,
        page_size,
        total_records,
        message="Success.",
        status_code=status.HTTP_200_OK,
    ):
        total_pages = (
            max(1, (total_records + page_size - 1) // page_size) if total_records else 1
        )
        payload = {
            "results": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_records": total_records,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
        }
        return self.success_response(
            data=payload, message=message, status_code=status_code
        )
