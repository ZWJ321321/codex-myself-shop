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
        order = Order.objects.create(
            order_no="OD202607010001",
            customer_name="张三",
            phone="13800138000",
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
        self.assertEqual(item.dish_name_snapshot, "焦糖布丁")
        self.assertEqual(item.line_total, Decimal("36.00"))
