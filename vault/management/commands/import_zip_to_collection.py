"""Management command to import a ZIP file as a new Collection."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from services.collections.import_zip import import_zip_as_new_collection

User = get_user_model()


class Command(BaseCommand):
    """Import a ZIP file as a new Collection."""

    help = "Import a ZIP file as a new Collection."

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "zip_path",
            type=str,
            help="Path to the ZIP file to import"
        )
        parser.add_argument(
            "--owner",
            type=int,
            help="User ID of collection owner",
            default=None
        )

    def handle(self, *args, **options):
        """Execute the command."""
        zip_path = options["zip_path"]
        owner_id = options.get("owner")
        owner = None

        if owner_id:
            try:
                owner = User.objects.get(pk=owner_id)
            except User.DoesNotExist as exc:
                raise CommandError(
                    f"Owner user ID not found: {owner_id}"
                ) from exc

        try:
            result = import_zip_as_new_collection(zip_path, owner=owner)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported collection '{result.collection.name}': "
                    f"files={result.created_files}, "
                    f"skipped={result.skipped_duplicates}, "
                    f"bytes={result.total_bytes}"
                )
            )
        except Exception as exc:
            raise CommandError(f"Import failed: {exc}") from exc
