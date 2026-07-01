from django.views import View

from apps.common.http import ok

from .models import Category, Dish


class CategoryListView(View):
    def get(self, request):
        rows = Category.objects.filter(is_active=True).values("id", "name", "slug", "sort_order")
        return ok(list(rows))


class DishListView(View):
    def get(self, request):
        dishes = Dish.objects.filter(is_available=True, category__is_active=True).select_related("category")
        category_slug = request.GET.get("category")
        if category_slug:
            dishes = dishes.filter(category__slug=category_slug)

        rows = [
            {
                "id": dish.id,
                "name": dish.name,
                "description": dish.description,
                "price": str(dish.price),
                "image_url": dish.image_url,
                "category": {
                    "id": dish.category_id,
                    "name": dish.category.name,
                    "slug": dish.category.slug,
                },
            }
            for dish in dishes
        ]
        return ok(rows)
