import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import ProductImage, Occasion


class Command(BaseCommand):
    help = "Uploads existing local /media images to Cloudinary and updates the DB references."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be uploaded without actually uploading anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.migrate_queryset(ProductImage.objects.all(), "image", dry_run)
        self.migrate_queryset(Occasion.objects.all(), "image", dry_run)

        self.stdout.write(self.style.SUCCESS("Migration complete."))

    def migrate_queryset(self, queryset, field_name, dry_run):
        total = queryset.count()
        self.stdout.write(f"\n--- {queryset.model.__name__}.{field_name} ({total} records) ---")

        migrated = skipped = failed = 0

        for obj in queryset:
            field = getattr(obj, field_name)

            if not field:
                skipped += 1
                continue

            local_path = os.path.join(settings.MEDIA_ROOT, field.name)

            if not os.path.exists(local_path):
                self.stdout.write(self.style.WARNING(f"  Missing on disk: {field.name}"))
                failed += 1
                continue

            if dry_run:
                self.stdout.write(f"  Would upload: {field.name}")
                migrated += 1
                continue

            try:
                with open(local_path, "rb") as f:
                    django_file = File(f, name=field.name)
                    # Re-save under the same relative name so the folder
                    # structure (category/product/color/view) is preserved on Cloudinary
                    field.save(field.name, django_file, save=True)
                self.stdout.write(f"  Uploaded: {field.name}")
                migrated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {obj} ({field.name}): {e}"))
                failed += 1

        self.stdout.write(f"Migrated: {migrated} | Skipped (empty): {skipped} | Failed: {failed}")