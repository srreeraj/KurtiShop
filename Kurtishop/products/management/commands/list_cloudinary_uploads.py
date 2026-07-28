# products/management/commands/list_cloudinary_uploads.py
import cloudinary.api
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Lists all resources currently uploaded to Cloudinary under media/products and media/categories."

    def add_arguments(self, parser):
        parser.add_argument(
            "--prefix",
            default="media/products/",
            help="Folder prefix to search under (e.g. media/products/, media/categories/)",
        )

    def handle(self, *args, **options):
        prefix = options["prefix"]
        resources = self.list_resources(prefix)

        self.stdout.write(f"Found {len(resources)} resources under '{prefix}':\n")
        for r in resources:
            self.stdout.write(f"  {r['public_id']}  ({r['format']}, {r['bytes']} bytes)")

    def list_resources(self, prefix, resource_type="image", max_results=500):
        resources = []
        next_cursor = None
        while True:
            params = {
                "type": "upload",
                "prefix": prefix,
                "resource_type": resource_type,
                "max_results": max_results,
            }
            if next_cursor:
                params["next_cursor"] = next_cursor

            result = cloudinary.api.resources(**params)
            resources.extend(result["resources"])
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
        return resources