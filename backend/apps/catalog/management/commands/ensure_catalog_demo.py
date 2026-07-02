from django.core.management.base import BaseCommand

from apps.catalog.demo_catalog import ensure_demo_catalog


class Command(BaseCommand):
    help = "Seed or repair the demo catalog used by the ordering page."

    def handle(self, *args, **options):
        summary = ensure_demo_catalog()
        if summary["skipped"]:
            self.stdout.write("Catalog already looks healthy. No demo repair needed.")
            return

        self.stdout.write(
            "Catalog repaired. "
            f"created_categories={summary['created_categories']} "
            f"updated_categories={summary['updated_categories']} "
            f"created_dishes={summary['created_dishes']} "
            f"updated_dishes={summary['updated_dishes']} "
            f"removed_debug_categories={summary['removed_debug_categories']} "
            f"removed_debug_dishes={summary['removed_debug_dishes']}"
        )
