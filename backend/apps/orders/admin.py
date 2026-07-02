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
    readonly_fields = ("order_no", "total_amount", "created_at", "updated_at")
    fieldsets = (
        ("点单人信息", {"fields": ("customer_name", "phone", "pickup_time", "dining_mode", "note")}),
        ("订单信息", {"fields": ("status", "order_no", "total_amount", "created_at", "updated_at")}),
    )
    inlines = [OrderItemInline]

    class Media:
        css = {"all": ("admin/orders.css",)}

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["status"].label = "订单状态"
        return form

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("items")

    @admin.display(description="状态", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span class="order-status-badge order-status-{}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )

    @admin.display(description="用餐方式", ordering="dining_mode")
    def dining_mode_label(self, obj):
        return obj.get_dining_mode_display()

    @admin.display(description="菜品摘要")
    def items_summary(self, obj):
        return "，".join(f"{item.dish_name_snapshot} x{item.quantity}" for item in obj.items.all()) or "-"
