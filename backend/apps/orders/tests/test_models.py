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

    def test_order_allows_missing_pickup_metadata_during_transition(self):
        order = Order.objects.create(
            order_no="OD202607010000",
            customer_name="李四",
            phone="13900139000",
            total_amount="0.00",
        )

        order.refresh_from_db()
        self.assertIsNone(order.pickup_time)
        self.assertIsNone(order.dining_mode)

    def test_order_stores_pickup_time_and_dining_mode(self):
        category = Category.objects.create(name="甜品", slug="dessert", is_active=True)
        dish = Dish.objects.create(category=category, name="焦糖布丁", price="36.00", is_available=True)
        pickup_time = timezone.now()
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

        order.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(order.pickup_time, pickup_time)
        self.assertEqual(order.dining_mode, Order.DiningMode.TAKEAWAY)
        self.assertEqual(item.dish_name_snapshot, "焦糖布丁")
        self.assertEqual(item.line_total, Decimal("36.00"))
