from datetime import timedelta
from unittest.mock import patch

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
            "pickup_time": timezone.localtime(timezone.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
            "dining_mode": "takeaway",
            "note": "少辣",
            "items": [{"dish_id": self.dish.id, "quantity": 2}],
        }
        payload.update(overrides)
        return payload

    def test_preview_returns_normalized_summary(self):
        pickup_time = "2030-01-01T18:00"
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(pickup_time=pickup_time),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["customer_name"], "李四")
        self.assertEqual(data["phone"], "13800138000")
        self.assertEqual(data["pickup_time"], pickup_time)
        self.assertEqual(data["dining_mode"], "takeaway")
        self.assertEqual(data["note"], "少辣")
        self.assertEqual(
            data["items"],
            [
                {
                    "dish_id": self.dish.id,
                    "dish_name": self.dish.name,
                    "unit_price": "68.00",
                    "quantity": 2,
                    "line_total": "136.00",
                }
            ],
        )
        self.assertEqual(data["total_amount"], "136.00")

    def test_create_order_persists_pickup_metadata_and_snapshots(self):
        pickup_time = "2030-01-01T18:00"
        response = self.client.post(
            "/api/orders",
            data=self.build_payload(
                pickup_time=pickup_time,
                expected_total_amount="136.00",
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        item = order.items.get()
        response_data = response.json()["data"]

        self.assertEqual(order.customer_name, "李四")
        self.assertEqual(order.phone, "13800138000")
        self.assertEqual(
            timezone.localtime(order.pickup_time).strftime("%Y-%m-%dT%H:%M"),
            pickup_time,
        )
        self.assertEqual(order.dining_mode, Order.DiningMode.TAKEAWAY)
        self.assertEqual(order.note, "少辣")
        self.assertEqual(item.dish_id, self.dish.id)
        self.assertEqual(item.dish_name_snapshot, self.dish.name)
        self.assertEqual(str(item.unit_price_snapshot), "68.00")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(str(item.line_total), "136.00")

        self.assertEqual(response_data["order_no"], order.order_no)
        self.assertEqual(response_data["customer_name"], "李四")
        self.assertEqual(response_data["phone"], "13800138000")
        self.assertEqual(response_data["pickup_time"], pickup_time)
        self.assertEqual(response_data["dining_mode"], "takeaway")
        self.assertEqual(response_data["note"], "少辣")
        self.assertEqual(response_data["items"][0]["dish_name"], self.dish.name)
        self.assertEqual(response_data["total_amount"], "136.00")

    def test_create_order_retries_when_generated_order_no_conflicts(self):
        Order.objects.create(
            order_no="OD202607010001",
            customer_name="已存在订单",
            phone="13800138001",
            pickup_time=timezone.now() + timedelta(hours=1),
            dining_mode=Order.DiningMode.TAKEAWAY,
            total_amount="68.00",
        )

        with patch(
            "apps.orders.services.generate_order_no",
            side_effect=["OD202607010001", "OD202607010002"],
        ):
            response = self.client.post(
                "/api/orders",
                data=self.build_payload(expected_total_amount="136.00"),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"]["order_no"], "OD202607010002")
        self.assertEqual(Order.objects.count(), 2)

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
        self.assertEqual(Order.objects.count(), 0)

    def test_preview_rejects_malformed_json(self):
        response = self.client.post(
            "/api/order-previews",
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "validation_error")

    def test_preview_rejects_non_object_payload(self):
        response = self.client.post(
            "/api/order-previews",
            data="[]",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "validation_error")

    def test_preview_rejects_items_when_not_a_list(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(items="not-a-list"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("items", body["errors"])

    def test_preview_rejects_items_when_row_is_not_an_object(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(items=[1]),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("items", body["errors"])

    def test_preview_rejects_past_pickup_time_and_invalid_dining_mode(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(
                pickup_time=timezone.localtime(timezone.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
                dining_mode="invalid-mode",
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("pickup_time", body["errors"])
        self.assertIn("dining_mode", body["errors"])

    def test_preview_rejects_invalid_pickup_time_format(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(pickup_time="2030/01/01 18:00"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("pickup_time", body["errors"])

    def test_preview_normalizes_null_note_to_empty_string(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(note=None),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["note"], "")

    def test_preview_rejects_null_customer_name(self):
        response = self.client.post(
            "/api/order-previews",
            data=self.build_payload(customer_name=None),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertEqual(body["code"], "validation_error")
        self.assertIn("customer_name", body["errors"])