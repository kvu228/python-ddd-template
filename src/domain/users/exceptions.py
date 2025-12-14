"""User domain exceptions."""


class UserDomainException(Exception):
    """Base exception for user domain."""

    pass


class UserNotFoundError(UserDomainException):
    """Raised when user is not found."""

    pass


class UserEmailAlreadyExistsError(UserDomainException):
    """Raised when user email already exists."""

    pass


class InvalidUserDataError(UserDomainException):
    """Raised when user data is invalid."""

    pass


