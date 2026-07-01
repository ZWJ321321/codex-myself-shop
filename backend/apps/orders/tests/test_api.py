from django.test import TestCase
from django.test.client import Client

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
        self.assertEqual(response.json()["code"], "validation_error")

    def test_create_order_accepts_json_without_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            "/api/orders/",
            data={
                "customer_name": "赵六",
                "phone": "13800138001",
                "note": "csrf回归测试",
                "items": [{"dish_id": self.dish.id, "quantity": 1}],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
