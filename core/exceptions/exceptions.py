"""Domain-specific exceptions exposed as structured API errors."""


class ApiError(Exception):
    """Base exception carrying an HTTP status and optional error details."""

    def __init__(self, message: str, status_code: int = 400, errors=None):
        """Initialize an error safe to expose through the API."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}


class BookNotAvailableError(ApiError):
    """Indicate that a book has no copies available to borrow."""

    def __init__(self, message: str = "Book is not available."):
        """Initialize the unavailable-book error."""
        super().__init__(message, status_code=400)


class InactiveMemberError(ApiError):
    """Indicate that an inactive member cannot borrow books."""

    def __init__(self, message: str = "Member is inactive."):
        """Initialize the inactive-member error."""
        super().__init__(message, status_code=400)


class InactiveBookError(ApiError):
    """Indicate that an inactive book cannot be borrowed."""

    def __init__(self, message: str = "Book is inactive."):
        """Initialize the inactive-book error."""
        super().__init__(message, status_code=400)


class LendingAlreadyReturnedError(ApiError):
    """Indicate an attempt to return an already returned lending."""

    def __init__(self, message: str = "Lending has already been returned."):
        """Initialize the duplicate-return error."""
        super().__init__(message, status_code=400)


class ActiveLendingError(ApiError):
    """Prevent deactivation of records that still participate in active loans."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409)
