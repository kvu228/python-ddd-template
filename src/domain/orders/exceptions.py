"""Order domain exceptions."""


class OrderDomainException(Exception):
    """Base exception for order domain."""

    pass


class OrderNotFoundError(OrderDomainException):
    """Raised when order is not found."""

    pass


class InvalidOrderDataError(OrderDomainException):
    """Raised when order data is invalid."""

    pass


class OrderCannotBeModifiedError(OrderDomainException):
    """Raised when order cannot be modified."""

    pass


class OrderItemNotFoundError(OrderDomainException):
    """Raised when order item is not found."""

    pass


