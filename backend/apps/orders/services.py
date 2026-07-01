from datetime import date
from decimal import Decimal

from django.db import transaction

from apps.catalog.models import Dish

from .models import Order, OrderItem


class OrderValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("order validation failed")


def generate_order_no(today=None):
    today = today or date.today()
    prefix = f"OD{today:%Y%m%d}"
    latest = (
        Order.objects.filter(order_no__startswith=prefix)
        .order_by("-order_no")
        .values_list("order_no", flat=True)
        .first()
    )
    next_number = 1 if not latest else int(latest[-4:]) + 1
    return f"{prefix}{next_number:04d}"


def _normalize_items(items):
    if not items:
        raise OrderValidationError({"items": ["购物车不能为空"]})

    normalized = []
    for row in items:
        dish_id = int(row.get("dish_id", 0))
        quantity = int(row.get("quantity", 0))
        if quantity <= 0:
            raise OrderValidationError({"items": ["菜品数量必须大于 0"]})

        dish = (
            Dish.objects.filter(id=dish_id, is_available=True, category__is_active=True)
            .select_related("category")
            .first()
        )
        if not dish:
            raise OrderValidationError({"items": [f"菜品 {dish_id} 不存在或已下架"]})

        line_total = dish.price * quantity
        normalized.append({"dish": dish, "quantity": quantity, "line_total": line_total})

    return normalized


def preview_order(payload):
    items = _normalize_items(payload.get("items", []))
    total_amount = sum((row["line_total"] for row in items), Decimal("0.00"))
    return {
        "items": [
            {
                "dish_id": row["dish"].id,
                "dish_name": row["dish"].name,
                "unit_price": str(row["dish"].price),
                "quantity": row["quantity"],
                "line_total": str(row["line_total"]),
            }
            for row in items
        ],
        "total_amount": str(total_amount),
    }


@transaction.atomic
def create_order(payload):
    customer_name = str(payload.get("customer_name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    note = str(payload.get("note", "")).strip()

    if not customer_name:
        raise OrderValidationError({"customer_name": ["姓名不能为空"]})
    if not phone:
        raise OrderValidationError({"phone": ["手机号不能为空"]})

    preview = preview_order(payload)
    order = Order.objects.create(
        order_no=generate_order_no(),
        customer_name=customer_name,
        phone=phone,
        note=note,
        total_amount=Decimal(preview["total_amount"]),
    )
    for row in preview["items"]:
        OrderItem.objects.create(
            order=order,
            dish_id=row["dish_id"],
            dish_name_snapshot=row["dish_name"],
            unit_price_snapshot=Decimal(row["unit_price"]),
            quantity=row["quantity"],
            line_total=Decimal(row["line_total"]),
        )
    return order, preview
