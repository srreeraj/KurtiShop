from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
from pathlib import Path
import os

from products.models import ProductImage, Occasion  # adjust if Occasion is in another app


class Command(BaseCommand):
    help = "Migrate existing local media files (ProductImage + Occasion) to Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show what would be migrated, do not upload or change DB",
        )
        parser.add_argument(
            "--delete-local",
            action="store_true",
            help="After successful upload, delete the local file (use with care)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        delete_local = options["delete_local"]

        self.stdout.write(self.style.WARNING("Starting media → Cloudinary migration"))
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN – nothing will be changed"))

        # ---------- ProductImage ----------
        self._migrate_queryset(
            ProductImage.objects.exclude(image="").exclude(image__isnull=True),
            field_name="image",
            dry_run=dry_run,
            delete_local=delete_local,
            label="ProductImage",
        )

        # ---------- Occasion ----------
        self._migrate_queryset(
            Occasion.objects.exclude(image="").exclude(image__isnull=True),
            field_name="image",
            dry_run=dry_run,
            delete_local=delete_local,
            label="Occasion",
        )

        self.stdout.write(self.style.SUCCESS("Done."))

    def _migrate_queryset(self, qs, field_name, dry_run, delete_local, label):
        total = qs.count()
        self.stdout.write(f"\n{label}: {total} records to check")

        migrated = 0
        skipped = 0
        errors = 0

        for obj in qs.iterator():
            field = getattr(obj, field_name)

            # Already on Cloudinary? (cloudinary storage returns a different kind of name)
            if not field.name or field.name.startswith("http") or "cloudinary" in str(field.storage):
                skipped += 1
                continue

            local_path = field.path  # absolute path on disk
            if not os.path.exists(local_path):
                self.stdout.write(self.style.ERROR(f"  Missing file: {local_path}"))
                errors += 1
                continue

            # Keep the same relative path so Cloudinary public_id looks familiar
            # e.g. products/category/product/color/front.jpg
            relative_name = field.name  # this is what was stored in DB

            self.stdout.write(f"  → {relative_name}")

            if dry_run:
                migrated += 1
                continue

            try:
                # Open the local file and re-save it through the new storage
                with open(local_path, "rb") as f:
                    # This will upload to Cloudinary and update the field
                    field.save(relative_name, f, save=False)

                obj.save(update_fields=[field_name])

                if delete_local:
                    try:
                        os.remove(local_path)
                        self.stdout.write(self.style.WARNING(f"    deleted local: {local_path}"))
                    except OSError as e:
                        self.stdout.write(self.style.ERROR(f"    could not delete local: {e}"))

                migrated += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ERROR: {e}"))
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{label} summary → migrated: {migrated}, skipped: {skipped}, errors: {errors}"
            )
        )