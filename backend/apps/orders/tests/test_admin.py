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
        self.assertEqual(self.admin.list_filter, ("status", "dining_mode", "created_at"))
        self.assertEqual(
            self.admin.fieldsets[0],
            ("点单人信息", {"fields": ("customer_name", "phone", "pickup_time", "dining_mode", "note")}),
        )

    def test_items_summary_renders_snapshot_names_and_quantities(self):
        self.assertEqual(self.admin.items_summary(self.order), "奶油南瓜鸡腿卷 x1")

    def test_pickup_fields_stay_editable_and_mode_uses_chinese_label(self):
        readonly = self.admin.get_readonly_fields(self.request, self.order)
        self.assertNotIn("pickup_time", readonly)
        self.assertNotIn("dining_mode", readonly)
        self.assertEqual(self.admin.dining_mode_label(self.order), "外带自取")

    def test_status_badge_uses_chinese_label_and_css_class(self):
        badge_html = self.admin.status_badge(self.order)
        self.assertIn("待处理", badge_html)
        self.assertIn("order-status-badge", badge_html)
        self.assertIn("order-status-pending", badge_html)

    def test_admin_media_loads_custom_admin_stylesheet(self):
        media_html = str(self.admin.media)
        self.assertIn("admin/orders.css", media_html)

    def test_status_field_uses_chinese_label_in_admin_form(self):
        form_class = self.admin.get_form(self.request, self.order)
        self.assertEqual(form_class.base_fields["status"].label, "订单状态")

    def test_order_fieldset_does_not_duplicate_editable_status_with_readonly_badge(self):
        self.assertEqual(
            self.admin.fieldsets[1],
            ("订单信息", {"fields": ("status", "order_no", "total_amount", "created_at", "updated_at")}),
        )
        self.assertNotIn("status_badge", self.admin.fieldsets[1][1]["fields"])
