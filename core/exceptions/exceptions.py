class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400, errors=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}


class BookNotAvailableError(ApiError):
    def __init__(self, message: str = "Book is not available."):
        super().__init__(message, status_code=400)


class InactiveMemberError(ApiError):
    def __init__(self, message: str = "Member is inactive."):
        super().__init__(message, status_code=400)


class InactiveBookError(ApiError):
    def __init__(self, message: str = "Book is inactive."):
        super().__init__(message, status_code=400)


class LendingAlreadyReturnedError(ApiError):
    def __init__(self, message: str = "Lending has already been returned."):
        super().__init__(message, status_code=400)
