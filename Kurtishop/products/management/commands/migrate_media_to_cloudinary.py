from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os

from products.models import ProductImage, Occasion
from categories.models import Category


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

        # ---------- Category ----------
        self._migrate_queryset(
            Category.objects.exclude(image="").exclude(image__isnull=True),
            field_name="image",
            dry_run=dry_run,
            delete_local=delete_local,
            label="Category",
        )

        self.stdout.write(self.style.SUCCESS("Done."))

    def _migrate_queryset(self, qs, field_name, dry_run, delete_local, label):
        total = qs.count()
        self.stdout.write(f"\n{label}: {total} records to check")

        migrated = 0
        skipped = 0
        errors = 0

        media_root = Path(settings.MEDIA_ROOT)

        for obj in qs.iterator():
            field = getattr(obj, field_name)
            relative_name = field.name  # e.g. products/kurtis/.../front.jpg

            if not relative_name:
                skipped += 1
                continue

            # Build the expected local path
            local_path = media_root / relative_name

            # Already on Cloudinary if the local file no longer exists
            # (or if the name looks like a full Cloudinary URL)
            if relative_name.startswith("http") or "res.cloudinary.com" in relative_name:
                skipped += 1
                continue

            if not local_path.exists():
                # File not on disk → either already migrated or missing
                skipped += 1
                continue

            self.stdout.write(f"  → {relative_name}")

            if dry_run:
                migrated += 1
                continue

            try:
                # Open local file and re-save through current storage (Cloudinary)
                with open(local_path, "rb") as f:
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
                self.stdout.write(self.style.ERROR(f"    ERROR on {relative_name}: {e}"))
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{label} summary → migrated: {migrated}, skipped: {skipped}, errors: {errors}"
            )
        )