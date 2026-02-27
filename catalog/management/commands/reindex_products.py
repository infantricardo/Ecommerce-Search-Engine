from django.core.management.base import BaseCommand

from catalog.models import Product
from catalog.search_engine import upsert_product_to_search


class Command(BaseCommand):
    help = "Reindex all products into Meilisearch."

    def handle(self, *args, **options):
        count = 0
        for product in Product.objects.all().iterator():
            upsert_product_to_search(product)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Reindexed {count} products."))
