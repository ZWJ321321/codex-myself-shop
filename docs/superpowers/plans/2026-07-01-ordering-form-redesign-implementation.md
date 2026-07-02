# Ordering Form Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the restaurant ordering flow into a two-step preview-and-submit experience with complete order metadata and MySQL-backed Django persistence.

**Architecture:** Keep the existing Vue 3 + Vite site structure and `/ordering` route, but replace the current ordering module with an explicit draft -> preview -> submit -> receipt state machine. Extend the Django `orders` domain with `pickup_time` and `dining_mode`, move the protocol to `POST /api/order-previews` and `POST /api/orders`, and let MySQL-backed services recompute prices on both preview and final submission.

**Tech Stack:** Vue 3, Vue Router, Vite, Node `--test`, Django 5, MySQL 8, PyMySQL

---

## File Map

- Verify only: `backend/config/settings.py`
- Modify: `backend/apps/common/http.py`
- Modify: `backend/apps/common/tests/test_project_smoke.py`
- Modify: `backend/apps/orders/models.py`
- Modify: `backend/apps/orders/services.py`
- Modify: `backend/apps/orders/views.py`
- Modify: `backend/apps/orders/urls.py`
- Modify: `backend/apps/orders/admin.py`
- Create: `backend/apps/orders/migrations/0002_order_pickup_time_order_dining_mode.py`
- Modify: `backend/apps/orders/tests/test_models.py`
- Modify: `backend/apps/orders/tests/test_api.py`
- Modify: `backend/apps/orders/tests/test_admin.py`
- Modify: `package.json`
- Modify: `page.test.mjs`
- Modify: `src/pages/OrderingPage.vue`
- Modify: `src/styles.css`
- Modify: `src/features/ordering/api.js`
- Modify: `src/features/ordering/state.js`
- Modify: `src/features/ordering/OrderingSection.vue`
- Create: `src/features/ordering/state.test.mjs`
- Create: `src/features/ordering/OrderPreviewPanel.vue`
- Create: `src/features/ordering/OrderReceiptCard.vue`

## Task 1: Extend Order Schema and Admin for Pickup Metadata

**Files:**
- Verify only: `backend/config/settings.py`
- Modify: `backend/apps/common/tests/test_project_smoke.py`
- Modify: `backend/apps/orders/models.py`
- Modify: `backend/apps/orders/admin.py`
- Modify: `backend/apps/orders/tests/test_models.py`
- Modify: `backend/apps/orders/tests/test_admin.py`
- Create: `backend/apps/orders/migrations/0002_order_pickup_time_order_dining_mode.py`

- [ ] **Step 1: Write the failing schema and admin tests**

```python
# backend/apps/common/tests/test_project_smoke.py
from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse


class ProjectSmokeTests(SimpleTestCase):
    def test_admin_route_exists(self):
        response = self.client.get(reverse("admin:login"))
        assert response.status_code == 200

    def test_mysql_engine_is_configured(self):
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"

    def test_mysql_charset_is_utf8mb4(self):
        assert settings.DATABASES["default"]["OPTIONS"]["charset"] == "utf8mb4"
```

```python
# backend/apps/orders/tests/test_models.py
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.catalog.models import Category, Dish
from apps.orders.models import Order, OrderItem
from apps.orders.services import generate_order_no


class OrderModelTests(TestCase):
    def test_generate_order_no_uses_od_prefix(self):
        order_no = generate_order_no()
        self.assertTrue(order_no.startswith("OD"))

    def test_order_stores_pickup_time_and_dining_mode(self):
        category = Category.objects.create(name="甜品", slug="dessert", is_active=True)
        dish = Dish.objects.create(category=category, name="焦糖布丁", price="36.00", is_available=True)
        pickup_time = timezone.now() + timedelta(hours=2)
        order = Order.objects.create(
            order_no="OD202607010001",
            customer_name="张三",
            phone="13800138000",
            pickup_time=pickup_time,
            dining_mode=Order.DiningMode.TAKEAWAY,
            total_amount="36.00",
        )
        item = OrderItem.objects.create(
            order=order,
            dish=dish,
            dish_name_snapshot=dish.name,
            unit_price_snapshot=Decimal("36.00"),
            quantity=1,
            line_total=Decimal("36.00"),
        )
        self.assertEqual(order.dining_mode, Order.DiningMode.TAKEAWAY)
        self.assertEqual(item.dish_name_snapshot, "焦糖布丁")
        self.assertEqual(item.line_total, Decimal("36.00"))
```

```python
# backend/apps/orders/tests/test_admin.py
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.catalog.models import Category, Dish
from apps.orders.admin import OrderAdmin
from apps.orders.models import Order, OrderItem


class OrderAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="热菜", slug="hot", is_active=True)
        dish = Dish.objects.create(
            category=category,
            name="奶油南瓜鸡腿卷",
            description="招牌菜",
            price="68.00",
            is_available=True,
            sort_order=1,
        )
        cls.order = Order.objects.create(
            order_no="OD202607010099",
            customer_name="张三",
            phone="13800138000",
            pickup_time=timezone.now(),
            dining_mode=Order.DiningMode.TAKEAWAY,
            note="少辣",
            status=Order.Status.PENDING,
            total_amount="68.00",
        )
        OrderItem.objects.create(
            order=cls.order,
            dish=dish,
            dish_name_snapshot=dish.name,
            unit_price_snapshot=Decimal("68.00"),
            quantity=1,
            line_total=Decimal("68.00"),
        )

    def setUp(self):
        self.admin = OrderAdmin(Order, AdminSite())
        self.request = RequestFactory().get("/admin/orders/order/")

    def test_list_display_and_fieldsets_include_pickup_metadata(self):
        self.assertEqual(
            self.admin.list_display,
            (
                "created_at",
                "order_no",
                "customer_name",
                "phone",
                "pickup_time",
                "dining_mode_label",
                "total_amount",
                "status_badge",
                "note",
                "items_summary",
            ),
        )
        self.assertEqual(
            self.admin.fieldsets,
            (
                ("点单人信息", {"fields": ("customer_name", "phone", "pickup_time", "dining_mode", "note")}),
                ("订单信息", {"fields": ("status", "status_badge", "order_no", "total_amount", "created_at", "updated_at")}),
            ),
        )

    def test_pickup_fields_stay_editable_and_mode_uses_chinese_label(self):
        readonly = self.admin.get_readonly_fields(self.request, self.order)
        self.assertNotIn("pickup_time", readonly)
        self.assertNotIn("dining_mode", readonly)
        self.assertEqual(self.admin.dining_mode_label(self.order), "外带自取")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python .\backend\manage.py test apps.common.tests.test_project_smoke apps.orders.tests.test_models apps.orders.tests.test_admin -v 2
```

Expected: FAIL because `Order` does not yet define `pickup_time` or `dining_mode`, and the admin layout still exposes the old field set.

- [ ] **Step 3: Implement the schema, migration, and admin updates**

```python
# backend/apps/orders/models.py
from django.db import models

from apps.common.models import TimeStampedModel


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待处理"
        CONFIRMED = "confirmed", "已确认"
        COMPLETED = "completed", "已完成"
        CANCELLED = "cancelled", "已取消"

    class DiningMode(models.TextChoices):
        TAKEAWAY = "takeaway", "外带自取"
        DINE_IN = "dine_in", "到店堂食"

    order_no = models.CharField(max_length=32, unique=True)
    customer_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    pickup_time = models.DateTimeField(db_index=True)
    dining_mode = models.CharField(max_length=20, choices=DiningMode.choices, db_index=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.order_no


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey("catalog.Dish", on_delete=models.PROTECT, related_name="order_items")
    dish_name_snapshot = models.CharField(max_length=120)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
```
```python
# backend/apps/orders/migrations/0002_order_pickup_time_order_dining_mode.py
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="pickup_time",
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="dining_mode",
            field=models.CharField(
                choices=[("takeaway", "外带自取"), ("dine_in", "到店堂食")],
                db_index=True,
                default="takeaway",
                max_length=20,
            ),
            preserve_default=False,
        ),
    ]
```

```python
# backend/apps/orders/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    verbose_name_plural = "菜品明细"
    readonly_fields = ("dish", "dish_name_snapshot", "unit_price_snapshot", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "order_no",
        "customer_name",
        "phone",
        "pickup_time",
        "dining_mode_label",
        "total_amount",
        "status_badge",
        "note",
        "items_summary",
    )
    list_filter = ("status", "dining_mode", "created_at")
    search_fields = ("order_no", "customer_name", "phone")
    ordering = ("-created_at", "-id")
    readonly_fields = ("status_badge", "order_no", "total_amount", "created_at", "updated_at")
    fieldsets = (
        ("点单人信息", {"fields": ("customer_name", "phone", "pickup_time", "dining_mode", "note")}),
        ("订单信息", {"fields": ("status", "status_badge", "order_no", "total_amount", "created_at", "updated_at")}),
    )
    inlines = [OrderItemInline]

    class Media:
        css = {"all": ("admin/orders.css",)}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("items")

    @admin.display(description="状态", ordering="status")
    def status_badge(self, obj):
        labels = {
            Order.Status.PENDING: "待处理",
            Order.Status.CONFIRMED: "已确认",
            Order.Status.COMPLETED: "已完成",
            Order.Status.CANCELLED: "已取消",
        }
        return format_html(
            '<span class="order-status-badge order-status-{}">{}</span>',
            obj.status,
            labels.get(obj.status, obj.status),
        )

    @admin.display(description="用餐方式", ordering="dining_mode")
    def dining_mode_label(self, obj):
        return obj.get_dining_mode_display()

    @admin.display(description="菜品摘要")
    def items_summary(self, obj):
        return "，".join(f"{item.dish_name_snapshot} x{item.quantity}" for item in obj.items.all()) or "-"
```

- [ ] **Step 4: Run migrations and verify the tests pass**

Run:

```powershell
python .\backend\manage.py migrate
python .\backend\manage.py test apps.common.tests.test_project_smoke apps.orders.tests.test_models apps.orders.tests.test_admin -v 2
```

Expected: the migration applies cleanly on MySQL, the smoke test confirms `utf8mb4`, and the order model/admin tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -- backend/apps/common/tests/test_project_smoke.py backend/apps/orders/models.py backend/apps/orders/admin.py backend/apps/orders/tests/test_models.py backend/apps/orders/tests/test_admin.py backend/apps/orders/migrations/0002_order_pickup_time_order_dining_mode.py
git commit -m "feat: add pickup metadata to orders"
```

## Task 2: Rebuild the Order Preview and Final Submission Contract

**Files:**
- Modify: `backend/apps/common/http.py`
- Modify: `backend/apps/orders/services.py`
- Modify: `backend/apps/orders/views.py`
- Modify: `backend/apps/orders/urls.py`
- Modify: `backend/apps/orders/tests/test_api.py`

- [ ] **Step 1: Write the failing API tests for the new contract**

```python
# backend/apps/orders/tests/test_api.py
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.catalog.models import Category, Dish
from apps.orders.models import Order


class OrderApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="热菜", slug="hot", is_active=True)
        cls.dish = Dish.objects.create(
            category=category,
            name="奶油南瓜鸡腿卷",
            description="招牌菜",
            price="68.00",
            is_available=True,
            sort_order=1,
        )

    def build_payload(self, **overrides):
        payload = {
            "customer_name": "李四",
            "phone": "13800138000",
            "pickup_time": (timezone.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
            "dining_mode": "takeaway",
            "note": "少辣",
            "items": [{"dish_id": self.dish.id, "quantity": 2}],
        }
        payload.update(overrides)
        return payload

    def test_preview_returns_normalized_summary(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["customer_name"], "李四")
        self.assertEqual(data["dining_mode"], "takeaway")
        self.assertEqual(data["items"][0]["line_total"], "136.00")
        self.assertEqual(data["total_amount"], "136.00")

    def test_create_order_persists_pickup_metadata_and_snapshots(self):
        payload = self.build_payload(expected_total_amount="136.00")
        response = self.client.post(
            "/api/orders",
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        self.assertEqual(order.dining_mode, Order.DiningMode.TAKEAWAY)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(response.json()["data"]["order_no"], order.order_no)

    def test_create_order_returns_price_changed_when_total_is_stale(self):
        response = self.client.post(
            "/api/orders",
            data=self.build_payload(expected_total_amount="135.00"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)
        body = response.json()
        self.assertEqual(body["code"], "price_changed")
        self.assertEqual(body["data"]["total_amount"], "136.00")

    def test_preview_rejects_past_pickup_time_and_invalid_dining_mode(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(
                pickup_time=(timezone.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
                dining_mode="invalid-mode",
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "validation_error")
        self.assertIn("pickup_time", response.json()["errors"])
        self.assertIn("dining_mode", response.json()["errors"])
```

- [ ] **Step 2: Run the API tests to verify they fail**

Run:

```powershell
python .\backend\manage.py test apps.orders.tests.test_api -v 2
```

Expected: FAIL because the code still exposes `/api/orders/preview/`, does not validate `pickup_time` or `dining_mode`, and does not implement `expected_total_amount` or `price_changed`.

- [ ] **Step 3: Implement the preview/create services, views, and routes**

```python
# backend/apps/common/http.py
from django.http import JsonResponse


def ok(data, message="success", status=200):
    return JsonResponse({"code": "ok", "message": message, "data": data}, status=status)


def fail(code, message, errors=None, data=None, status=400):
    payload = {"code": code, "message": message}
    if errors is not None:
        payload["errors"] = errors
    if data is not None:
        payload["data"] = data
    return JsonResponse(payload, status=status)
```

```python
# backend/apps/orders/services.py
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.catalog.models import Dish

from .models import Order, OrderItem

PHONE_RE = re.compile(r"^1\d{10}$")


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


def _normalize_contact_fields(payload):
    customer_name = str(payload.get("customer_name", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    pickup_raw = str(payload.get("pickup_time", "")).strip()
    dining_mode = str(payload.get("dining_mode", "")).strip()
    note = str(payload.get("note", "")).strip()
    errors = {}

    if not customer_name:
        errors["customer_name"] = ["请输入姓名"]
    if not PHONE_RE.match(phone):
        errors["phone"] = ["请输入 11 位手机号"]

    pickup_time = parse_datetime(pickup_raw)
    if pickup_time and timezone.is_naive(pickup_time):
        pickup_time = timezone.make_aware(pickup_time, timezone.get_current_timezone())
    if not pickup_raw or pickup_time is None:
        errors["pickup_time"] = ["请选择有效的取餐时间"]
    elif pickup_time <= timezone.now():
        errors["pickup_time"] = ["取餐时间必须晚于当前时间"]

    if dining_mode not in {Order.DiningMode.TAKEAWAY, Order.DiningMode.DINE_IN}:
        errors["dining_mode"] = ["请选择用餐方式"]

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
    if not items:
        raise OrderValidationError({"items": ["请至少选择一道菜"]})

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


def _normalize_expected_total(raw_value):
    try:
        return Decimal(str(raw_value).strip())
    except (InvalidOperation, ValueError):
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


@transaction.atomic
def create_order(payload):
    contact, items, summary = build_order_summary(payload)
    expected_total_amount = _normalize_expected_total(payload.get("expected_total_amount"))
    actual_total_amount = Decimal(summary["total_amount"])

    if actual_total_amount != expected_total_amount:
        raise OrderPriceChangedError(summary)

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
```

```python
# backend/apps/orders/views.py
import json

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.common.http import fail, ok

from .services import OrderPriceChangedError, OrderValidationError, create_order, preview_order


@method_decorator(csrf_exempt, name="dispatch")
class OrderPreviewView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            return ok(preview_order(payload))
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", errors=exc.errors, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class OrderCreateView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            order, summary = create_order(payload)
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", errors=exc.errors, status=400)
        except OrderPriceChangedError as exc:
            return fail("price_changed", "订单金额已变化，请重新确认", data=exc.summary, status=409)
        return ok({"order_no": order.order_no, **summary}, status=201)
```

```python
# backend/apps/orders/urls.py
from django.urls import path

from .views import OrderCreateView, OrderPreviewView

urlpatterns = [
    path("order-previews", OrderPreviewView.as_view(), name="order-preview"),
    path("orders", OrderCreateView.as_view(), name="order-create"),
]
```

- [ ] **Step 4: Run the API tests and the combined backend suite**

Run:

```powershell
python .\backend\manage.py test apps.orders.tests.test_api -v 2
python .\backend\manage.py test apps.common.tests.test_project_smoke apps.catalog.tests.test_api apps.orders.tests.test_models apps.orders.tests.test_api apps.orders.tests.test_admin -v 2
```

Expected: the preview and create-order endpoints PASS with the new paths, validation errors remain structured, and stale totals return HTTP `409` with `code = "price_changed"`.

- [ ] **Step 5: Commit**

```bash
git add -- backend/apps/common/http.py backend/apps/orders/services.py backend/apps/orders/views.py backend/apps/orders/urls.py backend/apps/orders/tests/test_api.py
git commit -m "feat: rebuild order preview contract"
```

## Task 3: Rebuild Frontend Ordering State and API Helpers

**Files:**
- Modify: `package.json`
- Modify: `src/features/ordering/api.js`
- Modify: `src/features/ordering/state.js`
- Create: `src/features/ordering/state.test.mjs`

- [ ] **Step 1: Write the failing Node tests for the new draft and API helpers**

```javascript
// src/features/ordering/state.test.mjs
import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildCreateOrderPayload,
  buildDraftSignature,
  buildPreviewPayload,
  estimateTotalAmount,
  validateOrderDraft,
} from './state.js';
import { createOrder, previewOrder } from './api.js';

test('ordering state builds preview and create payloads from the same draft', () => {
  const form = {
    customerName: '张三',
    phone: '13800138000',
    pickupTime: '2026-07-01T18:30',
    diningMode: 'takeaway',
    note: '少辣',
  };
  const cartItems = [{ dishId: 3, name: '招牌烤鸡', price: '68.00', quantity: 2 }];

  assert.equal(estimateTotalAmount(cartItems), '136.00');
  assert.deepEqual(buildPreviewPayload(form, cartItems), {
    customer_name: '张三',
    phone: '13800138000',
    pickup_time: '2026-07-01T18:30',
    dining_mode: 'takeaway',
    note: '少辣',
    items: [{ dish_id: 3, quantity: 2 }],
  });
  assert.equal(
    buildDraftSignature(form, cartItems),
    JSON.stringify(buildPreviewPayload(form, cartItems))
  );
  assert.deepEqual(buildCreateOrderPayload(form, cartItems, { total_amount: '136.00' }), {
    customer_name: '张三',
    phone: '13800138000',
    pickup_time: '2026-07-01T18:30',
    dining_mode: 'takeaway',
    note: '少辣',
    expected_total_amount: '136.00',
    items: [{ dish_id: 3, quantity: 2 }],
  });
});

test('ordering state rejects empty carts, invalid phones, and past pickup times', () => {
  const errors = validateOrderDraft(
    {
      customerName: '',
      phone: '123',
      pickupTime: '2026-06-30T10:00',
      diningMode: '',
      note: '',
    },
    [],
    new Date('2026-07-01T12:00:00')
  );

  assert.deepEqual(errors, {
    customerName: '请输入姓名',
    phone: '请输入 11 位手机号',
    pickupTime: '取餐时间必须晚于当前时间',
    diningMode: '请选择用餐方式',
    items: '请至少选择一道菜',
  });
});

test('ordering api helpers use the new endpoints and surface price_changed payloads', async () => {
  const originalFetch = globalThis.fetch;

  try {
    globalThis.fetch = async () => ({
      ok: false,
      status: 409,
      text: async () => JSON.stringify({
        code: 'price_changed',
        message: '订单金额已变化，请重新确认',
        data: { total_amount: '138.00', items: [] },
      }),
    });

    await assert.rejects(
      createOrder({ expected_total_amount: '136.00' }),
      (error) => error.code === 'price_changed' && error.data.total_amount === '138.00'
    );

    globalThis.fetch = async (url, options) => ({
      ok: true,
      status: 200,
      text: async () => JSON.stringify({ code: 'ok', message: 'success', data: { echo: { url, method: options.method } } }),
    });

    const preview = await previewOrder({ customer_name: '张三', items: [] });
    assert.equal(preview.data.echo.url, '/api/order-previews');
    assert.equal(preview.data.echo.method, 'POST');
  } finally {
    globalThis.fetch = originalFetch;
  }
});
```

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "node --test page.test.mjs src/features/ordering/state.test.mjs"
  }
}
```

- [ ] **Step 2: Run the frontend tests to verify they fail**

Run:

```powershell
npm run test
```

Expected: FAIL because `state.js` does not yet understand `pickupTime`, `diningMode`, or `expected_total_amount`, and `api.js` still posts to the old endpoints.

- [ ] **Step 3: Implement the frontend state and API helper layer**

```javascript
// src/features/ordering/state.js
const DINING_MODES = new Set(['takeaway', 'dine_in']);
const PHONE_RE = /^1\d{10}$/;

export function estimateTotalAmount(cartItems) {
  return cartItems.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0).toFixed(2);
}

export function buildPreviewPayload(form, cartItems) {
  return {
    customer_name: form.customerName.trim(),
    phone: form.phone.trim(),
    pickup_time: form.pickupTime,
    dining_mode: form.diningMode,
    note: form.note.trim(),
    items: cartItems.map((item) => ({ dish_id: item.dishId, quantity: item.quantity })),
  };
}

export function buildCreateOrderPayload(form, cartItems, summary) {
  return {
    ...buildPreviewPayload(form, cartItems),
    expected_total_amount: summary.total_amount,
  };
}

export function buildDraftSignature(form, cartItems) {
  return JSON.stringify(buildPreviewPayload(form, cartItems));
}

export function validateOrderDraft(form, cartItems, now = new Date()) {
  const errors = {};
  const pickupDate = form.pickupTime ? new Date(form.pickupTime) : null;

  if (!form.customerName.trim()) {
    errors.customerName = '请输入姓名';
  }
  if (!PHONE_RE.test(form.phone.trim())) {
    errors.phone = '请输入 11 位手机号';
  }
  if (!form.pickupTime) {
    errors.pickupTime = '请选择取餐时间';
  } else if (Number.isNaN(pickupDate?.getTime()) || pickupDate <= now) {
    errors.pickupTime = '取餐时间必须晚于当前时间';
  }
  if (!DINING_MODES.has(form.diningMode)) {
    errors.diningMode = '请选择用餐方式';
  }
  if (!cartItems.length) {
    errors.items = '请至少选择一道菜';
  }

  return errors;
}
```

```javascript
// src/features/ordering/api.js
function buildApiError(body, fallbackMessage) {
  const error = new Error(body?.message || fallbackMessage);
  error.code = body?.code || 'request_failed';
  error.errors = body?.errors || {};
  error.data = body?.data || null;
  return error;
}

export async function requestJson(url, options = {}, fallbackMessage = '请求失败') {
  let response;

  try {
    response = await fetch(url, options);
  } catch {
    throw new Error(fallbackMessage);
  }

  let body = null;
  try {
    const raw = await response.text();
    body = raw.trim() ? JSON.parse(raw) : null;
  } catch {
    body = null;
  }

  if (!response.ok) {
    throw buildApiError(body, fallbackMessage);
  }
  if (!body || typeof body !== 'object') {
    throw new Error(fallbackMessage);
  }
  return body;
}

export function fetchCategories() {
  return requestJson('/api/categories/', {}, '加载分类失败');
}

export function fetchDishes() {
  return requestJson('/api/dishes/', {}, '加载菜品失败');
}

export function previewOrder(payload) {
  return requestJson(
    '/api/order-previews',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    '确认订单信息失败'
  );
}

export function createOrder(payload) {
  return requestJson(
    '/api/orders',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
    '正式下单失败'
  );
}
```

- [ ] **Step 4: Run the frontend helper tests**

Run:

```powershell
npm run test
```

Expected: the new `state.test.mjs` PASSes, `page.test.mjs` still PASSes, and the test command becomes the standard frontend verification entrypoint.

- [ ] **Step 5: Commit**

```bash
git add -- package.json src/features/ordering/api.js src/features/ordering/state.js src/features/ordering/state.test.mjs
git commit -m "test: cover ordering draft helpers"
```

## Task 4: Replace the Ordering UI with the Two-Step Flow

**Files:**
- Modify: `page.test.mjs`
- Modify: `src/pages/OrderingPage.vue`
- Modify: `src/styles.css`
- Modify: `src/features/ordering/OrderingSection.vue`
- Create: `src/features/ordering/OrderPreviewPanel.vue`
- Create: `src/features/ordering/OrderReceiptCard.vue`

- [ ] **Step 1: Write the failing route-level regression checks**

```javascript
// page.test.mjs
test('ordering route exposes the new two-step ordering flow', async () => {
  const [pkgRaw, orderingPage, orderingSection, previewPanel, receiptCard, api] = await Promise.all([
    read('./package.json'),
    read('./src/pages/OrderingPage.vue'),
    read('./src/features/ordering/OrderingSection.vue'),
    read('./src/features/ordering/OrderPreviewPanel.vue'),
    read('./src/features/ordering/OrderReceiptCard.vue'),
    read('./src/features/ordering/api.js'),
  ]);

  const pkg = JSON.parse(pkgRaw);

  assert.equal(pkg.scripts.test, 'node --test page.test.mjs src/features/ordering/state.test.mjs');
  assert.match(orderingPage, /先确认价格，再正式下单/);
  assert.match(orderingSection, /previewOrder\(/);
  assert.match(orderingSection, /createOrder\(/);
  assert.match(orderingSection, /订单信息已变更，请重新确认价格/);
  assert.match(orderingSection, /取餐时间/);
  assert.match(orderingSection, /用餐方式/);
  assert.match(previewPanel, /确认订单信息/);
  assert.match(previewPanel, /正式下单/);
  assert.match(receiptCard, /订单回执/);
  assert.match(api, /order-previews/);
  assert.match(api, /正式下单失败/);
});
```

- [ ] **Step 2: Run the route-level tests to verify they fail**

Run:

```powershell
npm run test
```

Expected: FAIL because the current ordering page still describes the old flow, and the preview/receipt components do not exist yet.

- [ ] **Step 3: Implement the new ordering page, state machine, and presentational panels**

```vue
<!-- src/pages/OrderingPage.vue -->
<script setup>
import OrderingSection from '../features/ordering/OrderingSection.vue';
import { useRevealSections } from '../composables/useRevealSections.js';

useRevealSections();
</script>

<template>
  <div class="page-stack ordering-page-shell">
    <section class="page-hero page-hero-compact section-shell" data-reveal>
      <p class="page-kicker">Online Ordering</p>
      <h1 class="page-title">先确认价格，再正式下单。</h1>
      <p class="page-summary">
        这个页面把实时选菜、联系人填写、后端确认金额和订单回执合成一个完整流程，不再沿用旧版直接提交表单。
      </p>
    </section>

    <OrderingSection />
  </div>
</template>
```

```vue
<!-- src/features/ordering/OrderPreviewPanel.vue -->
<script setup>
const props = defineProps({
  summary: { type: Object, required: true },
  submitting: { type: Boolean, default: false },
  message: { type: String, default: '' },
});

const emit = defineEmits(['submit-order']);
</script>

<template>
  <section class="ordering-panel ordering-preview-panel">
    <div class="ordering-panel-header">
      <p class="ordering-panel-kicker">Confirmed by Server</p>
      <h3>确认订单信息</h3>
    </div>
    <p class="ordering-preview-copy">以下价格以后端最新菜单复算结果为准。</p>

    <div v-for="item in props.summary.items" :key="item.dish_id" class="ordering-preview-row">
      <div>
        <strong>{{ item.dish_name }}</strong>
        <p>¥{{ item.unit_price }} x {{ item.quantity }}</p>
      </div>
      <strong>¥{{ item.line_total }}</strong>
    </div>

    <dl class="ordering-preview-meta">
      <div><dt>联系人</dt><dd>{{ props.summary.customer_name }}</dd></div>
      <div><dt>手机号</dt><dd>{{ props.summary.phone }}</dd></div>
      <div><dt>取餐时间</dt><dd>{{ props.summary.pickup_time }}</dd></div>
      <div><dt>用餐方式</dt><dd>{{ props.summary.dining_mode === 'takeaway' ? '外带自取' : '到店堂食' }}</dd></div>
    </dl>

    <p v-if="props.summary.note" class="ordering-preview-note">备注：{{ props.summary.note }}</p>
    <p class="ordering-preview-total">确认总价：¥{{ props.summary.total_amount }}</p>
    <p v-if="props.message" class="ordering-inline-message">{{ props.message }}</p>

    <button class="button" type="button" :disabled="props.submitting" @click="emit('submit-order')">
      {{ props.submitting ? '正式下单中...' : '正式下单' }}
    </button>
  </section>
</template>
```

```vue
<!-- src/features/ordering/OrderReceiptCard.vue -->
<script setup>
const props = defineProps({
  receipt: { type: Object, required: true },
});
</script>

<template>
  <section class="ordering-panel ordering-receipt-card">
    <div class="ordering-panel-header">
      <p class="ordering-panel-kicker">Order Created</p>
      <h3>订单回执</h3>
    </div>

    <dl class="ordering-preview-meta">
      <div><dt>订单号</dt><dd>{{ props.receipt.order_no }}</dd></div>
      <div><dt>联系人</dt><dd>{{ props.receipt.customer_name }}</dd></div>
      <div><dt>手机号</dt><dd>{{ props.receipt.phone }}</dd></div>
      <div><dt>取餐时间</dt><dd>{{ props.receipt.pickup_time }}</dd></div>
      <div><dt>用餐方式</dt><dd>{{ props.receipt.dining_mode === 'takeaway' ? '外带自取' : '到店堂食' }}</dd></div>
    </dl>

    <div v-for="item in props.receipt.items" :key="item.dish_id" class="ordering-preview-row">
      <div>
        <strong>{{ item.dish_name }}</strong>
        <p>¥{{ item.unit_price }} x {{ item.quantity }}</p>
      </div>
      <strong>¥{{ item.line_total }}</strong>
    </div>

    <p class="ordering-preview-total">最终总价：¥{{ props.receipt.total_amount }}</p>
    <p v-if="props.receipt.note" class="ordering-preview-note">备注：{{ props.receipt.note }}</p>
  </section>
</template>
```

```vue
<!-- src/features/ordering/OrderingSection.vue -->
<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

import OrderPreviewPanel from './OrderPreviewPanel.vue';
import OrderReceiptCard from './OrderReceiptCard.vue';
import { createOrder, fetchCategories, fetchDishes, previewOrder } from './api.js';
import {
  buildCreateOrderPayload,
  buildDraftSignature,
  buildPreviewPayload,
  estimateTotalAmount,
  validateOrderDraft,
} from './state.js';

const stage = ref('editing');
const categories = ref([]);
const dishes = ref([]);
const cartItems = ref([]);
const loading = ref(true);
const loadError = ref('');
const submitMessage = ref('');
const fieldErrors = ref({});
const previewSummary = ref(null);
const previewSignature = ref('');
const receipt = ref(null);

const form = reactive({
  customerName: '',
  phone: '',
  pickupTime: '',
  diningMode: 'takeaway',
  note: '',
});

const estimatedTotal = computed(() => estimateTotalAmount(cartItems.value));

onMounted(async () => {
  try {
    const [categoryResponse, dishResponse] = await Promise.all([fetchCategories(), fetchDishes()]);
    categories.value = categoryResponse.data;
    dishes.value = dishResponse.data;
  } catch (error) {
    loadError.value = error.message || '加载点餐信息失败';
  } finally {
    loading.value = false;
  }
});

function invalidatePreview(message = '订单信息已变更，请重新确认价格。') {
  if (stage.value === 'preview_ready') {
    stage.value = 'editing';
    submitMessage.value = message;
  }
}

function handleAddDish(dish) {
  const existing = cartItems.value.find((item) => item.dishId === dish.id);
  cartItems.value = existing
    ? cartItems.value.map((item) =>
        item.dishId === dish.id ? { ...item, quantity: item.quantity + 1 } : item
      )
    : [...cartItems.value, { dishId: dish.id, name: dish.name, price: dish.price, quantity: 1 }];
  invalidatePreview();
}

function updateQuantity(dishId, quantity) {
  cartItems.value = quantity <= 0
    ? cartItems.value.filter((item) => item.dishId !== dishId)
    : cartItems.value.map((item) => (item.dishId === dishId ? { ...item, quantity } : item));
  invalidatePreview();
}

function updateField(field, value) {
  form[field] = value;
  invalidatePreview();
}

async function handlePreview() {
  submitMessage.value = '';
  fieldErrors.value = validateOrderDraft(form, cartItems.value);
  if (Object.keys(fieldErrors.value).length) {
    return;
  }

  stage.value = 'previewing';
  try {
    const result = await previewOrder(buildPreviewPayload(form, cartItems.value));
    previewSummary.value = result.data;
    previewSignature.value = buildDraftSignature(form, cartItems.value);
    stage.value = 'preview_ready';
  } catch (error) {
    stage.value = 'editing';
    fieldErrors.value = error.errors || {};
    submitMessage.value = error.message || '确认订单信息失败';
  }
}

async function handleSubmit() {
  if (buildDraftSignature(form, cartItems.value) !== previewSignature.value) {
    stage.value = 'editing';
    submitMessage.value = '订单信息已变更，请重新确认价格。';
    return;
  }

  stage.value = 'submitting';
  try {
    const result = await createOrder(buildCreateOrderPayload(form, cartItems.value, previewSummary.value));
    receipt.value = result.data;
    stage.value = 'success';
    cartItems.value = [];
  } catch (error) {
    if (error.code === 'price_changed' && error.data) {
      previewSummary.value = error.data;
      previewSignature.value = buildDraftSignature(form, cartItems.value);
      stage.value = 'preview_ready';
      submitMessage.value = error.message;
      return;
    }
    stage.value = 'preview_ready';
    fieldErrors.value = error.errors || {};
    submitMessage.value = error.message || '正式下单失败';
  }
}
</script>

<template>
  <section id="ordering" class="ordering section-shell" data-reveal>
    <div class="section-heading">
      <p class="eyebrow">Online Ordering</p>
      <h2>在线点餐</h2>
    </div>

    <p v-if="loadError" class="ordering-error">{{ loadError }}</p>

    <div v-else class="ordering-grid ordering-grid-rebuilt">
      <div class="ordering-menu-panel">
        <div class="ordering-category-row" v-if="categories.length">
          <span v-for="category in categories" :key="category.id" class="ordering-chip">{{ category.name }}</span>
        </div>

        <p v-if="loading" class="ordering-muted">正在加载菜单...</p>

        <div v-else class="ordering-dish-grid">
          <article v-for="dish in dishes" :key="dish.id" class="ordering-dish-card">
            <div class="ordering-dish-copy">
              <p class="dish-tag">{{ dish.category.name }}</p>
              <h3>{{ dish.name }}</h3>
              <p>{{ dish.description || '当日现做，适合当前页面的即时下单流程。' }}</p>
            </div>
            <div class="ordering-dish-meta">
              <strong>¥{{ dish.price }}</strong>
              <button class="button button-small" type="button" @click="handleAddDish(dish)">加入订单</button>
            </div>
          </article>
        </div>
      </div>

      <aside class="ordering-sidebar-panel">
        <section class="ordering-panel ordering-draft-panel">
          <div class="ordering-panel-header">
            <p class="ordering-panel-kicker">Draft Order</p>
            <h3>填写订单信息</h3>
          </div>

          <p v-if="fieldErrors.items" class="ordering-error">{{ fieldErrors.items }}</p>

          <div v-for="item in cartItems" :key="item.dishId" class="ordering-cart-row">
            <div>
              <strong>{{ item.name }}</strong>
              <p>¥{{ item.price }}</p>
            </div>
            <div class="ordering-cart-actions">
              <button type="button" @click="updateQuantity(item.dishId, item.quantity - 1)">-</button>
              <span>{{ item.quantity }}</span>
              <button type="button" @click="updateQuantity(item.dishId, item.quantity + 1)">+</button>
            </div>
          </div>

          <p v-if="!cartItems.length" class="ordering-muted">还没选菜，先加入一道招牌菜。</p>
          <p class="ordering-total">预计总价：¥{{ estimatedTotal }}</p>

          <div class="ordering-form-grid">
            <label class="ordering-field">
              <span>姓名</span>
              <input :value="form.customerName" class="ordering-input" type="text" @input="updateField('customerName', $event.target.value)" />
              <small v-if="fieldErrors.customerName" class="ordering-error">{{ fieldErrors.customerName }}</small>
            </label>

            <label class="ordering-field">
              <span>手机号</span>
              <input :value="form.phone" class="ordering-input" type="text" @input="updateField('phone', $event.target.value)" />
              <small v-if="fieldErrors.phone" class="ordering-error">{{ fieldErrors.phone }}</small>
            </label>

            <label class="ordering-field">
              <span>取餐时间</span>
              <input :value="form.pickupTime" class="ordering-input" type="datetime-local" @input="updateField('pickupTime', $event.target.value)" />
              <small v-if="fieldErrors.pickupTime" class="ordering-error">{{ fieldErrors.pickupTime }}</small>
            </label>

            <label class="ordering-field">
              <span>用餐方式</span>
              <select :value="form.diningMode" class="ordering-input" @change="updateField('diningMode', $event.target.value)">
                <option value="takeaway">外带自取</option>
                <option value="dine_in">到店堂食</option>
              </select>
              <small v-if="fieldErrors.diningMode" class="ordering-error">{{ fieldErrors.diningMode }}</small>
            </label>

            <label class="ordering-field ordering-field-full">
              <span>备注</span>
              <textarea :value="form.note" class="ordering-input ordering-textarea" rows="3" @input="updateField('note', $event.target.value)"></textarea>
            </label>
          </div>

          <p v-if="submitMessage && stage === 'editing'" class="ordering-inline-message">{{ submitMessage }}</p>

          <button class="button" type="button" :disabled="stage === 'previewing'" @click="handlePreview">
            {{ stage === 'previewing' ? '确认中...' : '确认订单信息' }}
          </button>
        </section>

        <OrderPreviewPanel
          v-if="previewSummary && stage !== 'success'"
          :summary="previewSummary"
          :submitting="stage === 'submitting'"
          :message="submitMessage"
          @submit-order="handleSubmit"
        />

        <OrderReceiptCard v-if="receipt && stage === 'success'" :receipt="receipt" />
      </aside>
    </div>
  </section>
</template>
```

```css
/* src/styles.css */
.ordering-grid-rebuilt {
  align-items: start;
}

.ordering-sidebar-panel {
  display: grid;
  gap: 18px;
  position: sticky;
  top: 96px;
}

.ordering-panel {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 249, 240, 0.92);
  border: 1px solid rgba(120, 72, 34, 0.12);
  box-shadow: 0 22px 60px rgba(64, 38, 16, 0.1);
}

.ordering-panel-header {
  display: grid;
  gap: 6px;
  margin-bottom: 16px;
}

.ordering-panel-kicker {
  margin: 0;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--accent-color);
  font-size: 0.72rem;
}

.ordering-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.ordering-field-full {
  grid-column: 1 / -1;
}

.ordering-preview-row,
.ordering-cart-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(120, 72, 34, 0.12);
}

.ordering-preview-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0;
}

.ordering-preview-meta dt {
  color: var(--text-soft);
  font-size: 0.85rem;
}

.ordering-preview-meta dd {
  margin: 4px 0 0;
  font-weight: 600;
}

.ordering-preview-total {
  margin: 16px 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.ordering-inline-message {
  margin: 12px 0 0;
  color: #9a4a19;
}

@media (max-width: 900px) {
  .ordering-sidebar-panel {
    position: static;
  }

  .ordering-form-grid,
  .ordering-preview-meta {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 4: Run automated and manual verification**

Run:

```powershell
npm run test
npm run build
python .\backend\manage.py test -v 2
```

Then start both dev servers:

```powershell
python .\backend\manage.py runserver
npm run dev
```

Expected:
- Automated tests PASS.
- Vite build succeeds.
- `/ordering` shows menu selection, contact form, preview confirmation, and receipt states.
- Editing a confirmed draft drops the UI back to `editing` and shows `订单信息已变更，请重新确认价格。`.
- A stale total returned by the backend is surfaced as a `price_changed` confirmation refresh instead of a silent failure.

- [ ] **Step 5: Commit**

```bash
git add -- page.test.mjs src/pages/OrderingPage.vue src/styles.css src/features/ordering/OrderingSection.vue src/features/ordering/OrderPreviewPanel.vue src/features/ordering/OrderReceiptCard.vue
git commit -m "feat: rebuild ordering flow ui"
```

## Self-Review Checklist

- Spec coverage:
  - MySQL as the default database and `utf8mb4` constraint: Task 1
  - New order metadata (`pickup_time`, `dining_mode`): Task 1
  - Preview endpoint, final submit endpoint, and `price_changed`: Task 2
  - Frontend real-time estimate plus backend confirmation payloads: Task 3
  - Draft -> preview -> submit -> receipt state machine: Task 4
  - Full automated and local verification: Task 4
- Placeholder scan:
  - No `TODO`, `TBD`, `implement later`, or “similar to Task N” shortcuts remain.
- Type consistency:
  - Frontend payload keys are `customer_name`, `phone`, `pickup_time`, `dining_mode`, `note`, `items`, `expected_total_amount`.
  - Backend service and API tests use the same keys and the same enum values: `takeaway`, `dine_in`.
  - Frontend stage values are `editing`, `previewing`, `preview_ready`, `submitting`, `success`.
