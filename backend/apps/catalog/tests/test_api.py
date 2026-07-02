from django.test import TestCase

from apps.catalog.models import Category, Dish


class CatalogApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hot = Category.objects.create(name="热菜", slug="hot", sort_order=1, is_active=True)
        Category.objects.create(name="隐藏", slug="hidden", sort_order=99, is_active=False)
        Dish.objects.create(
            category=cls.hot,
            name="慢炖番茄牛肉锅",
            description="热菜",
            price="88.00",
            image_url="https://example.com/beef.jpg",
            is_available=True,
            sort_order=1,
        )

    def test_categories_endpoint_returns_only_active_categories(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["slug"], "hot")
        self.assertEqual(len(response.json()["data"]), 1)

    def test_dishes_endpoint_can_filter_by_category_slug(self):
        response = self.client.get("/api/dishes/?category=hot")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"][0]["name"], "慢炖番茄牛肉锅")
