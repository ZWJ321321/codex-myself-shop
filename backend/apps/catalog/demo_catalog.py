from decimal import Decimal
import re

from django.db import transaction

from .models import Category, Dish


DEMO_CATALOG = (
    {
        "slug": "main-course",
        "name": "主菜",
        "sort_order": 1,
        "dish": {
            "name": "炙烤南瓜奶油鸡腿排",
            "description": "奶香南瓜底配现烤鸡腿排，适合第一次来先点这道。",
            "price": Decimal("68.00"),
            "sort_order": 1,
        },
    },
    {
        "slug": "stew-pot",
        "name": "锅物",
        "sort_order": 2,
        "dish": {
            "name": "慢炖番茄牛肉锅",
            "description": "番茄汁慢炖牛肉与蔬菜，适合两人边聊边吃。",
            "price": Decimal("88.00"),
            "sort_order": 1,
        },
    },
    {
        "slug": "dessert-drink",
        "name": "甜点饮品",
        "sort_order": 3,
        "dish": {
            "name": "海盐焦糖巴斯克配冷萃",
            "description": "甜点和饮品一次配齐，适合作为整单收尾。",
            "price": Decimal("36.00"),
            "sort_order": 1,
        },
    },
)

DEMO_SLUGS = {entry["slug"] for entry in DEMO_CATALOG}
QUESTION_MARK_TEXT = re.compile(r"^[?？�\d\s\-_/.,:;()]+$")


def looks_garbled_text(value):
    text = (value or "").strip()
    if not text:
        return True
    return bool(QUESTION_MARK_TEXT.fullmatch(text))


def catalog_needs_repair():
    if not Category.objects.exists() or not Dish.objects.exists():
        return True
    if Category.objects.filter(slug__startswith="hot-debug").exists():
        return True
    if Dish.objects.filter(category__slug__startswith="hot-debug").exists():
        return True

    for category in Category.objects.filter(slug__in=DEMO_SLUGS).only("name"):
        if looks_garbled_text(category.name):
            return True

    dishes = Dish.objects.filter(category__slug__in=DEMO_SLUGS).select_related("category").only(
        "name",
        "description",
        "category__slug",
    )
    for dish in dishes:
        if looks_garbled_text(dish.name) or looks_garbled_text(dish.description):
            return True

    return False


@transaction.atomic
def ensure_demo_catalog():
    summary = {
        "created_categories": 0,
        "updated_categories": 0,
        "created_dishes": 0,
        "updated_dishes": 0,
        "removed_debug_categories": 0,
        "removed_debug_dishes": 0,
        "changed": False,
        "skipped": False,
    }
    if not catalog_needs_repair():
        summary["skipped"] = True
        return summary

    debug_dishes = Dish.objects.filter(category__slug__startswith="hot-debug")
    summary["removed_debug_dishes"] = debug_dishes.count()
    if summary["removed_debug_dishes"]:
        debug_dishes.delete()
        summary["changed"] = True

    debug_categories = Category.objects.filter(slug__startswith="hot-debug")
    summary["removed_debug_categories"] = debug_categories.count()
    if summary["removed_debug_categories"]:
        debug_categories.delete()
        summary["changed"] = True

    for entry in DEMO_CATALOG:
        category, category_created = Category.objects.get_or_create(
            slug=entry["slug"],
            defaults={
                "name": entry["name"],
                "sort_order": entry["sort_order"],
                "is_active": True,
            },
        )
        if category_created:
            summary["created_categories"] += 1
            summary["changed"] = True
        else:
            changed_fields = []
            if looks_garbled_text(category.name) and category.name != entry["name"]:
                category.name = entry["name"]
                changed_fields.append("name")
            if category.sort_order != entry["sort_order"]:
                category.sort_order = entry["sort_order"]
                changed_fields.append("sort_order")
            if not category.is_active:
                category.is_active = True
                changed_fields.append("is_active")
            if changed_fields:
                category.save(update_fields=changed_fields)
                summary["updated_categories"] += 1
                summary["changed"] = True

        dish = Dish.objects.filter(category=category).order_by("sort_order", "id").first()
        if dish is None:
            Dish.objects.create(
                category=category,
                name=entry["dish"]["name"],
                description=entry["dish"]["description"],
                price=entry["dish"]["price"],
                image_url="",
                is_available=True,
                sort_order=entry["dish"]["sort_order"],
            )
            summary["created_dishes"] += 1
            summary["changed"] = True
            continue

        if looks_garbled_text(dish.name) or looks_garbled_text(dish.description):
            dish.name = entry["dish"]["name"]
            dish.description = entry["dish"]["description"]
            dish.price = entry["dish"]["price"]
            dish.sort_order = entry["dish"]["sort_order"]
            dish.is_available = True
            dish.save(update_fields=["name", "description", "price", "sort_order", "is_available"])
            summary["updated_dishes"] += 1
            summary["changed"] = True

    return summary
