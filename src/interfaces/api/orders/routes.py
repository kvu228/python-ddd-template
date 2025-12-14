"""Order API routes."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.orders.commands import (
    AddOrderItemCommand,
    ConfirmOrderCommand,
    CreateOrderCommand,
    RemoveOrderItemCommand,
)
from src.application.orders.dto import ShippingAddressDTO
from src.domain.orders.exceptions import OrderNotFoundError
from src.application.orders.service import OrderApplicationService
from src.interfaces.api.dependencies import get_order_service
from src.interfaces.api.orders.schemas import (
    AddOrderItemRequest,
    CreateOrderRequest,
    OrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def create_order(
    request: CreateOrderRequest,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderResponse:
    """Create a new order.

    Args:
        request: Order creation data
        service: Order application service

    Returns:
        Created order data
    """
    command = CreateOrderCommand(
        user_id=request.user_id,
        shipping_address=ShippingAddressDTO(
            street=request.shipping_address.street,
            city=request.shipping_address.city,
            state=request.shipping_address.state,
            zip_code=request.shipping_address.zip_code,
            country=request.shipping_address.country,
        ),
    )
    order_dto = service.create_order(command)
    return OrderResponse(**order_dto.__dict__)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
)
async def get_order(
    order_id: UUID,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderResponse:
    """Get order by ID.

    Args:
        order_id: Order identifier
        service: Order application service

    Returns:
        Order data

    Raises:
        HTTPException: If order is not found
    """
    order_dto = service.get_order(order_id)
    if not order_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return OrderResponse(**order_dto.__dict__)


@router.post(
    "/{order_id}/items",
    response_model=OrderResponse,
    summary="Add item to order",
)
async def add_item_to_order(
    order_id: UUID,
    request: AddOrderItemRequest,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderResponse:
    """Add an item to an order.

    Args:
        order_id: Order identifier
        request: Item data
        service: Order application service

    Returns:
        Updated order data

    Raises:
        HTTPException: If order is not found or cannot be modified
    """
    try:
        command = AddOrderItemCommand(
            order_id=order_id,
            product_id=request.product_id,
            product_name=request.product_name,
            price=request.price,
            currency=request.currency,
            quantity=request.quantity,
        )
        order_dto = service.add_item_to_order(command)
        return OrderResponse(**order_dto.__dict__)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.delete(
    "/{order_id}/items/{item_id}",
    response_model=OrderResponse,
    summary="Remove item from order",
)
async def remove_item_from_order(
    order_id: UUID,
    item_id: UUID,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderResponse:
    """Remove an item from an order.

    Args:
        order_id: Order identifier
        item_id: Item identifier
        service: Order application service

    Returns:
        Updated order data

    Raises:
        HTTPException: If order or item is not found
    """
    try:
        command = RemoveOrderItemCommand(order_id=order_id, item_id=item_id)
        order_dto = service.remove_item_from_order(command)
        return OrderResponse(**order_dto.__dict__)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.patch(
    "/{order_id}/confirm",
    response_model=OrderResponse,
    summary="Confirm order",
)
async def confirm_order(
    order_id: UUID,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderResponse:
    """Confirm an order.

    Args:
        order_id: Order identifier
        service: Order application service

    Returns:
        Updated order data

    Raises:
        HTTPException: If order is not found or cannot be confirmed
    """
    try:
        command = ConfirmOrderCommand(order_id=order_id)
        order_dto = service.confirm_order(command)
        return OrderResponse(**order_dto.__dict__)
    except OrderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

