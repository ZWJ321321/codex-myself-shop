from django.db import models

from apps.common.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "菜品分类"
        verbose_name_plural = "菜品分类"

    def __str__(self):
        return self.name


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
        verbose_name = "菜品"
        verbose_name_plural = "菜品"

    def __str__(self):
        return self.name
