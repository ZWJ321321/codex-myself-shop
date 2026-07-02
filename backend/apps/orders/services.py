from datetime import date
from decimal import Decimal, InvalidOperation
import re

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.catalog.models import Dish

from .models import Order, OrderItem


PHONE_RE = re.compile(r"^1\d{10}$")
ORDER_NO_RETRY_LIMIT = 5


class OrderValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("order validation failed")


class OrderPriceChangedError(Exception):
    def __init__(self, summary):
        self.summary = summary
        super().__init__("order price changed")


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


def _format_pickup_time(value):
    return timezone.localtime(value).strftime("%Y-%m-%dT%H:%M")


def _normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _normalize_contact_fields(payload):
    errors = {}

    customer_name = _normalize_text(payload.get("customer_name"))
    if not customer_name:
        errors["customer_name"] = ["请输入联系人姓名"]

    phone = _normalize_text(payload.get("phone"))
    if not PHONE_RE.match(phone):
        errors["phone"] = ["请输入正确的手机号"]

    raw_pickup_time = _normalize_text(payload.get("pickup_time"))
    pickup_time = parse_datetime(raw_pickup_time) if raw_pickup_time else None
    if pickup_time is None:
        errors["pickup_time"] = ["请选择有效的取餐时间"]
    else:
        current_timezone = timezone.get_current_timezone()
        if timezone.is_naive(pickup_time):
            pickup_time = timezone.make_aware(pickup_time, current_timezone)
        else:
            pickup_time = timezone.localtime(pickup_time, current_timezone)
        if pickup_time <= timezone.now():
            errors["pickup_time"] = ["取餐时间必须晚于当前时间"]

    dining_mode = _normalize_text(payload.get("dining_mode"))
    allowed_modes = {Order.DiningMode.TAKEAWAY, Order.DiningMode.DINE_IN}
    if dining_mode not in allowed_modes:
        errors["dining_mode"] = ["请选择有效的用餐方式"]

    note = _normalize_text(payload.get("note"))

    if errors:
        raise OrderValidationError(errors)

    return {
        "customer_name": customer_name,
        "phone": phone,
        "pickup_time": pickup_time,
        "dining_mode": dining_mode,
        "note": note,
    }


def _normalize_items(items):
    if not isinstance(items, list):
        raise OrderValidationError({"items": ["菜品列表格式不正确"]})
    if not items:
        raise OrderValidationError({"items": ["购物车不能为空"]})

    normalized = []
    for row in items:
        if not isinstance(row, dict):
            raise OrderValidationError({"items": ["菜品数据格式不正确"]})

        try:
            dish_id = int(row.get("dish_id", 0))
        except (TypeError, ValueError):
            raise OrderValidationError({"items": ["菜品不存在或已下架"]})

        try:
            quantity = int(row.get("quantity", 0))
        except (TypeError, ValueError):
            raise OrderValidationError({"items": ["菜品数量必须大于 0"]})

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


def _normalize_expected_total(raw_value):
    try:
        return Decimal(str(raw_value))
    except (InvalidOperation, TypeError, ValueError):
        raise OrderValidationError({"expected_total_amount": ["请先确认订单金额"]})


def build_order_summary(payload):
    contact = _normalize_contact_fields(payload)
    items = _normalize_items(payload.get("items", []))
    total_amount = sum((row["line_total"] for row in items), Decimal("0.00"))
    summary = {
        "customer_name": contact["customer_name"],
        "phone": contact["phone"],
        "pickup_time": _format_pickup_time(contact["pickup_time"]),
        "dining_mode": contact["dining_mode"],
        "note": contact["note"],
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
    return contact, items, summary


def preview_order(payload):
    _, _, summary = build_order_summary(payload)
    return summary


def create_order(payload):
    contact, items, summary = build_order_summary(payload)
    expected_total_amount = _normalize_expected_total(payload.get("expected_total_amount"))
    actual_total_amount = Decimal(summary["total_amount"])
    if actual_total_amount != expected_total_amount:
        raise OrderPriceChangedError(summary)

    last_error = None
    for _ in range(ORDER_NO_RETRY_LIMIT):
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    order_no=generate_order_no(),
                    customer_name=contact["customer_name"],
                    phone=contact["phone"],
                    pickup_time=contact["pickup_time"],
                    dining_mode=contact["dining_mode"],
                    note=contact["note"],
                    total_amount=actual_total_amount,
                )
                for row in items:
                    OrderItem.objects.create(
                        order=order,
                        dish=row["dish"],
                        dish_name_snapshot=row["dish"].name,
                        unit_price_snapshot=row["dish"].price,
                        quantity=row["quantity"],
                        line_total=row["line_total"],
                    )
                return order, summary
        except IntegrityError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise RuntimeError("failed to create order")