class AppError(Exception):
    """Base exception for business and domain errors."""


class ConflictError(AppError):
    """Entity already exists."""


class UnauthorizedError(AppError):
    """Authentication failed."""


class ForbiddenError(AppError):
    """User has no rights for this operation."""


class NotFoundError(AppError):
    """Entity was not found."""


class ExternalServiceError(AppError):
    """External service call failed."""
