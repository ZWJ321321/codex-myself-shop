# Django Ordering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django + MySQL ordering backend and embed menu, cart, and order submission into the existing Vue single-page restaurant site.

**Architecture:** Keep the current Vue 3 + Vite landing page and insert one ordering section into the same page. Add a separate `backend/` Django project with `catalog` and `orders` apps, expose JSON APIs under `/api/`, and let the Vue page keep cart state locally while Django validates prices and writes orders transactionally to MySQL.

**Tech Stack:** Vue 3, Vite, Django, MySQL, PyMySQL, Node `--test`, Django `manage.py test`

---

## File Map

- Modify: `.gitignore`
- Modify: `vite.config.js`
- Modify: `src/App.vue`
- Modify: `src/styles.css`
- Modify: `page.test.mjs`
- Create: `src/features/ordering/api.js`
- Create: `src/features/ordering/state.js`
- Create: `src/features/ordering/OrderingSection.vue`
- Create: `backend/requirements.txt`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/asgi.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/apps/common/__init__.py`
- Create: `backend/apps/common/apps.py`
- Create: `backend/apps/common/models.py`
- Create: `backend/apps/common/http.py`
- Create: `backend/apps/common/tests/__init__.py`
- Create: `backend/apps/common/tests/test_project_smoke.py`
- Create: `backend/apps/catalog/__init__.py`
- Create: `backend/apps/catalog/apps.py`
- Create: `backend/apps/catalog/models.py`
- Create: `backend/apps/catalog/admin.py`
- Create: `backend/apps/catalog/views.py`
- Create: `backend/apps/catalog/urls.py`
- Create: `backend/apps/catalog/migrations/__init__.py`
- Create: `backend/apps/catalog/tests/__init__.py`
- Create: `backend/apps/catalog/tests/test_api.py`
- Create: `backend/apps/orders/__init__.py`
- Create: `backend/apps/orders/apps.py`
- Create: `backend/apps/orders/models.py`
- Create: `backend/apps/orders/admin.py`
- Create: `backend/apps/orders/services.py`
- Create: `backend/apps/orders/views.py`
- Create: `backend/apps/orders/urls.py`
- Create: `backend/apps/orders/migrations/__init__.py`
- Create: `backend/apps/orders/tests/__init__.py`
- Create: `backend/apps/orders/tests/test_models.py`
- Create: `backend/apps/orders/tests/test_api.py`

## Task 1: Bootstrap Django + MySQL Project

**Files:**
- Modify: `.gitignore`
- Create: `backend/requirements.txt`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/asgi.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/apps/common/__init__.py`
- Create: `backend/apps/common/apps.py`
- Create: `backend/apps/common/models.py`
- Create: `backend/apps/common/http.py`
- Test: `backend/apps/common/tests/test_project_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from django.test import SimpleTestCase
from django.urls import reverse
from django.conf import settings


class ProjectSmokeTests(SimpleTestCase):
    def test_admin_route_exists(self):
        response = self.client.get(reverse("admin:login"))
        assert response.status_code == 200

    def test_mysql_engine_is_configured(self):
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python .\backend\manage.py test apps.common.tests.test_project_smoke -v 2`

Expected: FAIL with an import or settings error because the Django project files do not exist yet.

- [ ] **Step 3: Write the minimal project scaffold**

```python
# backend/requirements.txt
Django>=5.1,<5.2
PyMySQL>=1.1,<1.2
```

```gitignore
# .gitignore
.codex/
.agents/
.idea/
node_modules/
dist/
preview*.png
Thumbs.db
.DS_Store
backend/.venv/
backend/__pycache__/
backend/**/__pycache__/
backend/.pytest_cache/
backend/.mypy_cache/
backend/.env
```

```python
# backend/manage.py
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

```python
# backend/config/__init__.py
import pymysql

pymysql.install_as_MySQLdb()
```

```python
# backend/config/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "restaurant_ordering"),
        "USER": os.getenv("MYSQL_USER", "root"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

```python
# backend/config/asgi.py
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
```

```python
# backend/config/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
```

```python
# backend/apps/common/apps.py
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
```

```python
# backend/apps/common/models.py
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

```python
# backend/apps/common/http.py
from django.http import JsonResponse


def ok(data, message="success", status=200):
    return JsonResponse({"code": "ok", "message": message, "data": data}, status=status)


def fail(code, message, errors=None, status=400):
    payload = {"code": code, "message": message}
    if errors:
        payload["errors"] = errors
    return JsonResponse(payload, status=status)
```

- [ ] **Step 4: Run tests and Django checks**

Run:

```powershell
python -m pip install -r .\backend\requirements.txt
python .\backend\manage.py test apps.common.tests.test_project_smoke -v 2
python .\backend\manage.py check
```

Expected: both commands PASS, and `System check identified no issues` appears.

- [ ] **Step 5: Commit**

```bash
git add .gitignore backend
git commit -m "feat: bootstrap django mysql backend"
```

## Task 2: Build Catalog Models, Admin, and Read APIs

**Files:**
- Create: `backend/apps/catalog/__init__.py`
- Create: `backend/apps/catalog/apps.py`
- Create: `backend/apps/catalog/models.py`
- Create: `backend/apps/catalog/admin.py`
- Create: `backend/apps/catalog/views.py`
- Create: `backend/apps/catalog/urls.py`
- Create: `backend/apps/catalog/migrations/__init__.py`
- Create: `backend/apps/catalog/tests/__init__.py`
- Create: `backend/apps/catalog/tests/test_api.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: Write the failing catalog API tests**

```python
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Category, Dish


class CatalogApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.noodle = Category.objects.create(name="热菜", slug="hot", sort_order=1, is_active=True)
        cls.hidden = Category.objects.create(name="隐藏", slug="hidden", sort_order=99, is_active=False)
        Dish.objects.create(
            category=cls.noodle,
            name="慢炖番茄牛肉锅",
            description="热菜",
            price="88.00",
            image_url="https://example.com/beef.jpg",
            is_available=True,
            sort_order=1,
        )

    def test_categories_endpoint_returns_only_active_categories(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["slug"], "hot")
        self.assertEqual(len(response.json()["data"]), 1)

    def test_dishes_endpoint_can_filter_by_category_slug(self):
        response = self.client.get("/api/dishes/?category=hot")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["name"], "慢炖番茄牛肉锅")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python .\backend\manage.py test apps.catalog.tests.test_api -v 2`

Expected: FAIL because `apps.catalog` is not installed and the `/api/` routes do not exist yet.

- [ ] **Step 3: Write the minimal catalog implementation**

```python
# backend/apps/catalog/models.py
from django.db import models

from apps.common.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]


class Dish(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="dishes")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["category__sort_order", "sort_order", "id"]
```

```python
# backend/apps/catalog/views.py
from django.views import View

from apps.catalog.models import Category, Dish
from apps.common.http import ok


class CategoryListView(View):
    def get(self, request):
        rows = Category.objects.filter(is_active=True).values("id", "name", "slug", "sort_order")
        return ok(list(rows))


class DishListView(View):
    def get(self, request):
        qs = Dish.objects.filter(is_available=True, category__is_active=True).select_related("category")
        category_slug = request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        rows = [{
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": str(dish.price),
            "image_url": dish.image_url,
            "category": {"id": dish.category_id, "name": dish.category.name, "slug": dish.category.slug},
        } for dish in qs]
        return ok(rows)
```

```python
# backend/apps/catalog/urls.py
from django.urls import path

from .views import CategoryListView, DishListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("dishes/", DishListView.as_view(), name="dish-list"),
]
```

```python
# backend/apps/catalog/admin.py
from django.contrib import admin

from .models import Category, Dish


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    ordering = ("sort_order", "id")


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "sort_order")
    list_filter = ("is_available", "category")
    search_fields = ("name",)
    ordering = ("category__sort_order", "sort_order", "id")
```

```python
# backend/config/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "apps.catalog",
]
```

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.catalog.urls")),
]
```

- [ ] **Step 4: Run migrations and tests**

Run:

```powershell
python .\backend\manage.py makemigrations catalog
python .\backend\manage.py migrate
python .\backend\manage.py test apps.catalog.tests.test_api -v 2
```

Expected: migration files are created, MySQL tables are applied, and both catalog API tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "feat: add catalog models and read apis"
```

## Task 3: Add Order Models, Numbering, and Admin

**Files:**
- Create: `backend/apps/orders/__init__.py`
- Create: `backend/apps/orders/apps.py`
- Create: `backend/apps/orders/models.py`
- Create: `backend/apps/orders/admin.py`
- Create: `backend/apps/orders/services.py`
- Create: `backend/apps/orders/migrations/__init__.py`
- Create: `backend/apps/orders/tests/__init__.py`
- Create: `backend/apps/orders/tests/test_models.py`
- Modify: `backend/config/settings.py`

- [ ] **Step 1: Write the failing order model tests**

```python
from decimal import Decimal

from django.test import TestCase

from apps.catalog.models import Category, Dish
from apps.orders.models import Order, OrderItem
from apps.orders.services import generate_order_no


class OrderModelTests(TestCase):
    def test_generate_order_no_uses_od_prefix(self):
        order_no = generate_order_no()
        self.assertTrue(order_no.startswith("OD"))

    def test_order_item_snapshot_persists_price_and_name(self):
        category = Category.objects.create(name="甜品", slug="dessert", is_active=True)
        dish = Dish.objects.create(category=category, name="焦糖布丁", price="36.00", is_available=True)
        order = Order.objects.create(order_no="OD202607010001", customer_name="张三", phone="13800138000", total_amount="36.00")
        item = OrderItem.objects.create(
            order=order,
            dish=dish,
            dish_name_snapshot=dish.name,
            unit_price_snapshot=Decimal("36.00"),
            quantity=1,
            line_total=Decimal("36.00"),
        )
        self.assertEqual(item.dish_name_snapshot, "焦糖布丁")
        self.assertEqual(item.line_total, Decimal("36.00"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python .\backend\manage.py test apps.orders.tests.test_models -v 2`

Expected: FAIL because the `orders` app, models, and services do not exist yet.

- [ ] **Step 3: Write the minimal order domain**

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

    order_no = models.CharField(max_length=32, unique=True)
    customer_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at", "-id"]


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey("catalog.Dish", on_delete=models.PROTECT, related_name="order_items")
    dish_name_snapshot = models.CharField(max_length=120)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
```

```python
# backend/apps/orders/services.py
from datetime import date

from apps.orders.models import Order


def generate_order_no(today=None):
    today = today or date.today()
    prefix = f"OD{today:%Y%m%d}"
    latest = Order.objects.filter(order_no__startswith=prefix).order_by("-order_no").values_list("order_no", flat=True).first()
    next_number = 1 if not latest else int(latest[-4:]) + 1
    return f"{prefix}{next_number:04d}"
```

```python
# backend/apps/orders/admin.py
from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("dish", "dish_name_snapshot", "unit_price_snapshot", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "customer_name", "phone", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_no", "customer_name", "phone")
    inlines = [OrderItemInline]
```

```python
# backend/config/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "apps.catalog",
    "apps.orders",
]
```

- [ ] **Step 4: Run migrations and model tests**

Run:

```powershell
python .\backend\manage.py makemigrations orders
python .\backend\manage.py migrate
python .\backend\manage.py test apps.orders.tests.test_models -v 2
```

Expected: order migrations apply cleanly and both model tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "feat: add order models and admin"
```

## Task 4: Implement Order Preview and Submission APIs

**Files:**
- Modify: `backend/apps/orders/services.py`
- Create: `backend/apps/orders/views.py`
- Create: `backend/apps/orders/urls.py`
- Create: `backend/apps/orders/tests/test_api.py`
- Modify: `backend/config/urls.py`

- [ ] **Step 1: Write the failing API tests**

```python
from django.test import TestCase

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

    def test_preview_recalculates_total(self):
        response = self.client.post(
            "/api/orders/preview/",
            data={"items": [{"dish_id": self.dish.id, "quantity": 2}]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["total_amount"], "136.00")

    def test_create_order_persists_order_and_items(self):
        response = self.client.post(
            "/api/orders/",
            data={
                "customer_name": "李四",
                "phone": "13800138000",
                "note": "少辣",
                "items": [{"dish_id": self.dish.id, "quantity": 2}],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().items.count(), 1)

    def test_create_order_rejects_empty_cart(self):
        response = self.client.post(
            "/api/orders/",
            data={"customer_name": "李四", "phone": "13800138000", "note": "", "items": []},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "validation_error")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python .\backend\manage.py test apps.orders.tests.test_api -v 2`

Expected: FAIL because the `/api/orders/preview/` and `/api/orders/` routes do not exist.

- [ ] **Step 3: Write the minimal transactional order service and views**

```python
# backend/apps/orders/services.py
from decimal import Decimal
import json

from django.db import transaction

from apps.catalog.models import Dish
from apps.orders.models import Order, OrderItem


class OrderValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("order validation failed")


def _normalize_items(items):
    if not items:
        raise OrderValidationError({"items": ["购物车不能为空"]})

    normalized = []
    for row in items:
        dish_id = int(row.get("dish_id", 0))
        quantity = int(row.get("quantity", 0))
        if quantity <= 0:
            raise OrderValidationError({"items": ["菜品数量必须大于 0"]})
        dish = Dish.objects.filter(id=dish_id, is_available=True, category__is_active=True).select_related("category").first()
        if not dish:
            raise OrderValidationError({"items": [f"菜品 {dish_id} 不存在或已下架"]})
        line_total = dish.price * quantity
        normalized.append({"dish": dish, "quantity": quantity, "line_total": line_total})
    return normalized


def preview_order(payload):
    items = _normalize_items(payload.get("items", []))
    total_amount = sum((row["line_total"] for row in items), Decimal("0.00"))
    return {
        "items": [{
            "dish_id": row["dish"].id,
            "dish_name": row["dish"].name,
            "unit_price": str(row["dish"].price),
            "quantity": row["quantity"],
            "line_total": str(row["line_total"]),
        } for row in items],
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
        total_amount=preview["total_amount"],
    )
    for row in preview["items"]:
        OrderItem.objects.create(
            order=order,
            dish_id=row["dish_id"],
            dish_name_snapshot=row["dish_name"],
            unit_price_snapshot=row["unit_price"],
            quantity=row["quantity"],
            line_total=row["line_total"],
        )
    return order, preview
```

```python
# backend/apps/orders/views.py
import json

from django.views import View

from apps.common.http import fail, ok
from apps.orders.services import OrderValidationError, create_order, preview_order


class OrderPreviewView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            return ok(preview_order(payload))
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)


class OrderCreateView(View):
    def post(self, request):
        payload = json.loads(request.body or "{}")
        try:
            order, preview = create_order(payload)
        except OrderValidationError as exc:
            return fail("validation_error", "提交数据不合法", exc.errors, status=400)
        return ok({"order_no": order.order_no, **preview}, status=201)
```

```python
# backend/apps/orders/urls.py
from django.urls import path

from .views import OrderCreateView, OrderPreviewView

urlpatterns = [
    path("orders/preview/", OrderPreviewView.as_view(), name="order-preview"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
]
```

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.orders.urls")),
]
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python .\backend\manage.py test apps.orders.tests.test_api -v 2
python .\backend\manage.py test apps.catalog.tests.test_api apps.orders.tests.test_models apps.orders.tests.test_api -v 2
```

Expected: preview and create order tests PASS, and the combined suite stays green.

- [ ] **Step 5: Commit**

```bash
git add backend
git commit -m "feat: add order preview and submit apis"
```

## Task 5: Integrate Ordering UI Into the Vue Single Page

**Files:**
- Modify: `src/App.vue`
- Create: `src/features/ordering/api.js`
- Create: `src/features/ordering/state.js`
- Create: `src/features/ordering/OrderingSection.vue`
- Modify: `src/styles.css`
- Modify: `vite.config.js`
- Modify: `page.test.mjs`

- [ ] **Step 1: Write the failing front-end tests**

```javascript
import { addCartItem, updateCartItemQuantity, buildOrderPayload, validateOrderDraft } from "./src/features/ordering/state.js";

test("ordering helpers manage cart and validate payloads", () => {
  const dish = { id: 7, name: "焦糖布丁", price: "36.00" };
  const once = addCartItem([], dish);
  const twice = addCartItem(once, dish);

  assert.equal(twice[0].quantity, 2);
  assert.equal(updateCartItemQuantity(twice, 7, 0).length, 0);

  assert.deepEqual(validateOrderDraft({ customerName: "", phone: "", note: "" }, []), {
    customerName: "请输入姓名",
    phone: "请输入手机号",
    items: "请至少选择一道菜",
  });

  assert.deepEqual(buildOrderPayload(
    { customerName: "张三", phone: "13800138000", note: "少冰" },
    [{ dishId: 7, quantity: 2 }]
  ), {
    customer_name: "张三",
    phone: "13800138000",
    note: "少冰",
    items: [{ dish_id: 7, quantity: 2 }],
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test .\page.test.mjs`

Expected: FAIL because `src/features/ordering/state.js` and the ordering section markup do not exist.

- [ ] **Step 3: Implement the front-end ordering module**

```javascript
// src/features/ordering/api.js
export async function fetchCategories() {
  const response = await fetch("/api/categories/");
  if (!response.ok) throw new Error("加载分类失败");
  return response.json();
}

export async function fetchDishes() {
  const response = await fetch("/api/dishes/");
  if (!response.ok) throw new Error("加载菜品失败");
  return response.json();
}

export async function submitOrder(payload) {
  const response = await fetch("/api/orders/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  if (!response.ok) throw body;
  return body;
}
```

```javascript
// src/features/ordering/state.js
export function addCartItem(cartItems, dish) {
  const existing = cartItems.find((item) => item.dishId === dish.id);
  if (!existing) {
    return [...cartItems, { dishId: dish.id, name: dish.name, price: dish.price, quantity: 1 }];
  }
  return cartItems.map((item) =>
    item.dishId === dish.id ? { ...item, quantity: item.quantity + 1 } : item
  );
}

export function updateCartItemQuantity(cartItems, dishId, quantity) {
  if (quantity <= 0) {
    return cartItems.filter((item) => item.dishId !== dishId);
  }
  return cartItems.map((item) => (item.dishId === dishId ? { ...item, quantity } : item));
}

export function validateOrderDraft(form, cartItems) {
  const errors = {};
  if (!form.customerName.trim()) errors.customerName = "请输入姓名";
  if (!form.phone.trim()) errors.phone = "请输入手机号";
  if (!cartItems.length) errors.items = "请至少选择一道菜";
  return errors;
}

export function buildOrderPayload(form, cartItems) {
  return {
    customer_name: form.customerName.trim(),
    phone: form.phone.trim(),
    note: form.note.trim(),
    items: cartItems.map((item) => ({ dish_id: item.dishId, quantity: item.quantity })),
  };
}
```

```vue
<!-- src/features/ordering/OrderingSection.vue -->
<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { fetchCategories, fetchDishes, submitOrder } from './api.js';
import { addCartItem, buildOrderPayload, updateCartItemQuantity, validateOrderDraft } from './state.js';

const categories = ref([]);
const dishes = ref([]);
const cartItems = ref([]);
const form = reactive({ customerName: '', phone: '', note: '' });
const errors = ref({});
const submitState = reactive({ loading: false, message: '', orderNo: '' });

const totalAmount = computed(() =>
  cartItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0).toFixed(2)
);

onMounted(async () => {
  const [categoryRes, dishRes] = await Promise.all([fetchCategories(), fetchDishes()]);
  categories.value = categoryRes.data;
  dishes.value = dishRes.data;
});

async function handleSubmit() {
  errors.value = validateOrderDraft(form, cartItems.value);
  if (Object.keys(errors.value).length) return;
  submitState.loading = true;
  try {
    const result = await submitOrder(buildOrderPayload(form, cartItems.value));
    submitState.orderNo = result.data.order_no;
    submitState.message = '订单提交成功';
    cartItems.value = [];
  } finally {
    submitState.loading = false;
  }
}
</script>

<template>
  <section id="ordering" class="ordering section-shell" data-reveal>
    <div class="section-heading">
      <p class="eyebrow">Online Ordering</p>
      <h2>在线点菜</h2>
    </div>
    <div class="ordering-grid">
      <div class="ordering-menu">
        <article v-for="dish in dishes" :key="dish.id" class="ordering-dish-card">
          <h3>{{ dish.name }}</h3>
          <p>{{ dish.description }}</p>
          <div class="ordering-dish-meta">
            <strong>￥{{ dish.price }}</strong>
            <button class="button button-small" type="button" @click="cartItems = addCartItem(cartItems, dish)">
              加入购物车
            </button>
          </div>
        </article>
      </div>
      <aside class="ordering-cart">
        <p v-if="errors.items" class="ordering-error">{{ errors.items }}</p>
        <div v-for="item in cartItems" :key="item.dishId" class="cart-row">
          <span>{{ item.name }}</span>
          <div class="cart-actions">
            <button type="button" @click="cartItems = updateCartItemQuantity(cartItems, item.dishId, item.quantity - 1)">-</button>
            <span>{{ item.quantity }}</span>
            <button type="button" @click="cartItems = updateCartItemQuantity(cartItems, item.dishId, item.quantity + 1)">+</button>
          </div>
        </div>
        <p class="ordering-total">合计：￥{{ totalAmount }}</p>
        <input v-model="form.customerName" class="ordering-input" placeholder="姓名" />
        <input v-model="form.phone" class="ordering-input" placeholder="手机号" />
        <textarea v-model="form.note" class="ordering-input ordering-textarea" placeholder="备注"></textarea>
        <button class="button" type="button" :disabled="submitState.loading" @click="handleSubmit">
          {{ submitState.loading ? '提交中...' : '提交订单' }}
        </button>
        <p v-if="submitState.orderNo" class="order-success">订单已提交，订单号 {{ submitState.orderNo }}</p>
      </aside>
    </div>
  </section>
</template>
```

```js
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  base: './',
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
```

```vue
<!-- src/App.vue -->
<script setup>
import OrderingSection from './features/ordering/OrderingSection.vue';
</script>

<template>
  <main>
    <!-- keep existing hero/story/dishes/space/highlights sections -->
    <OrderingSection />
    <!-- keep existing contact section -->
  </main>
</template>
```

```javascript
// page.test.mjs
test('ordering section is wired into the Vue app', async () => {
  const [app, ordering] = await Promise.all([
    readFile(new URL('./src/App.vue', import.meta.url), 'utf8'),
    readFile(new URL('./src/features/ordering/OrderingSection.vue', import.meta.url), 'utf8'),
  ]);

  assert.match(app, /OrderingSection/);
  assert.match(ordering, /id="ordering"/);
  assert.match(ordering, /提交订单/);
});
```

- [ ] **Step 4: Run the front-end test and build checks**

Run:

```powershell
node --test .\page.test.mjs
npm run build
```

Expected: the Node test PASSes, Vite build succeeds, and the ordering section is bundled into `dist/`.

- [ ] **Step 5: Commit**

```bash
git add src vite.config.js page.test.mjs
git commit -m "feat: add single-page ordering ui"
```

## Task 6: Verify End-to-End Behavior and Tighten Admin/Data Flow

**Files:**
- Modify: `backend/apps/orders/admin.py`
- Modify: `backend/apps/orders/services.py`
- Modify: `src/features/ordering/OrderingSection.vue`
- Modify: `src/styles.css`
- Modify: `page.test.mjs`

- [ ] **Step 1: Write one failing regression test for down-shelved dishes**

```python
def test_create_order_rejects_unavailable_dish(self):
    self.dish.is_available = False
    self.dish.save(update_fields=["is_available"])
    response = self.client.post(
        "/api/orders/",
        data={
            "customer_name": "王五",
            "phone": "13800138000",
            "note": "",
            "items": [{"dish_id": self.dish.id, "quantity": 1}],
        },
        content_type="application/json",
    )
    self.assertEqual(response.status_code, 400)
```

- [ ] **Step 2: Run regression tests and local servers**

Run:

```powershell
python .\backend\manage.py test apps.orders.tests.test_api -v 2
python .\backend\manage.py runserver
npm run dev
```

Expected: the new test fails if service logic regressed; after the fix, the test passes and both local servers start without config errors.

- [ ] **Step 3: Apply the final polish**

```python
# backend/apps/orders/admin.py
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_no", "customer_name", "phone", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_no", "customer_name", "phone")
    readonly_fields = ("order_no", "customer_name", "phone", "note", "total_amount", "created_at", "updated_at")
    inlines = [OrderItemInline]
```

```vue
<!-- src/features/ordering/OrderingSection.vue -->
<template>
  <section id="ordering" class="ordering section-shell" data-reveal>
    <div class="section-heading">
      <p class="eyebrow">Online Ordering</p>
      <h2>在线点菜</h2>
    </div>
    <p v-if="submitState.orderNo" class="order-success">
      订单已提交，订单号 {{ submitState.orderNo }}
    </p>
  </section>
</template>
```

```css
/* src/styles.css */
.ordering-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 22px;
}

.order-success {
  color: var(--brand);
  font-weight: 600;
}
```

- [ ] **Step 4: Run the full verification suite**

Run:

```powershell
python .\backend\manage.py test -v 2
node --test .\page.test.mjs
npm run build
```

Expected: all Django tests PASS, the Node test PASSes, and the production build succeeds with no new warnings that block release.

- [ ] **Step 5: Commit**

```bash
git add backend src page.test.mjs
git commit -m "test: verify mysql ordering flow end to end"
```

## Self-Review Checklist

- Spec coverage:
  - Django backend bootstrap: Task 1
  - Category and dish admin/read APIs: Task 2
  - Order models, snapshots, status, order number: Task 3
  - Preview and create-order API, validation, transaction: Task 4
  - Same-page Vue ordering UI and Vite proxy: Task 5
  - Regression checks and final verification: Task 6
- Placeholder scan:
  - No `TODO`, `TBD`, or “similar to task N” shortcuts remain.
- Type consistency:
  - Front-end payload uses `customer_name`, `phone`, `note`, `items[].dish_id`, `items[].quantity`
  - Back-end preview and create endpoints expect the same keys
  - Order status values remain `pending`, `confirmed`, `completed`, `cancelled`
