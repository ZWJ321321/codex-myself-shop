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
