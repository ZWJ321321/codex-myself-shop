from django.core.management import call_command
from django.test import TestCase

from apps.catalog.models import Category, Dish


class EnsureCatalogDemoCommandTests(TestCase):
    def test_command_seeds_demo_menu_when_catalog_is_empty(self):
        call_command("ensure_catalog_demo")

        categories = list(Category.objects.order_by("sort_order", "id").values_list("slug", "name"))
        dishes = list(Dish.objects.order_by("category__sort_order", "sort_order", "id").values_list("name", flat=True))

        self.assertEqual(
            categories,
            [
                ("main-course", "主菜"),
                ("stew-pot", "锅物"),
                ("dessert-drink", "甜点饮品"),
            ],
        )
        self.assertEqual(
            dishes,
            [
                "炙烤南瓜奶油鸡腿排",
                "慢炖番茄牛肉锅",
                "海盐焦糖巴斯克配冷萃",
            ],
        )

    def test_command_repairs_garbled_demo_rows_and_removes_debug_rows(self):
        main_course = Category.objects.create(name="??", slug="main-course", sort_order=99, is_active=True)
        Dish.objects.create(
            category=main_course,
            name="?????????",
            description="????????????????????????",
            price="68.00",
            is_available=True,
            sort_order=9,
        )
        debug_category = Category.objects.create(name="??2", slug="hot-debug-1782899149", sort_order=0, is_active=True)
        Dish.objects.create(
            category=debug_category,
            name="???????",
            description="???",
            price="68.00",
            is_available=True,
            sort_order=0,
        )

        call_command("ensure_catalog_demo")

        main_course.refresh_from_db()
        repaired_dish = Dish.objects.get(category=main_course)

        self.assertEqual(main_course.name, "主菜")
        self.assertEqual(main_course.sort_order, 1)
        self.assertEqual(repaired_dish.name, "炙烤南瓜奶油鸡腿排")
        self.assertEqual(repaired_dish.description, "奶香南瓜底配现烤鸡腿排，适合第一次来先点这道。")
        self.assertEqual(repaired_dish.sort_order, 1)
        self.assertFalse(Category.objects.filter(slug__startswith="hot-debug").exists())
        self.assertFalse(Dish.objects.filter(category__slug__startswith="hot-debug").exists())

    def test_command_keeps_existing_readable_menu(self):
        category = Category.objects.create(name="主厨推荐", slug="main-course", sort_order=7, is_active=True)
        Dish.objects.create(
            category=category,
            name="香煎鸡排",
            description="现点现做",
            price="66.00",
            is_available=True,
            sort_order=3,
        )

        call_command("ensure_catalog_demo")

        category.refresh_from_db()
        dish = Dish.objects.get(category=category)

        self.assertEqual(category.name, "主厨推荐")
        self.assertEqual(category.sort_order, 7)
        self.assertEqual(dish.name, "香煎鸡排")
        self.assertEqual(dish.description, "现点现做")
        self.assertEqual(dish.sort_order, 3)
