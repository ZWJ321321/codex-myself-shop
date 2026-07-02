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
    pickup_time = models.DateTimeField(db_index=True, null=True, blank=True)
    dining_mode = models.CharField(max_length=20, choices=DiningMode.choices, db_index=True, null=True, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "订单"
        verbose_name_plural = "订单"

    def __str__(self):
        return self.order_no


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey("catalog.Dish", on_delete=models.PROTECT, related_name="order_items")
    dish_name_snapshot = models.CharField(max_length=120)
    unit_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "订单菜品"
        verbose_name_plural = "订单菜品"
