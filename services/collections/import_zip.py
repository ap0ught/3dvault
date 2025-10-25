"""ZIP to Collection import service.

This module provides functionality to import ZIP archives as new Collections
in the 3D Vault system. It includes safety checks for zip-slip and zip-bomb
attacks, file deduplication, and integration with history/email systems.
"""

from __future__ import annotations

import hashlib
import os
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from vault.models import Collection, EmailQueue, UserHistory, VaultFile

User = get_user_model()


def _get_max_entries() -> int:
    """Get maximum number of entries allowed in a ZIP."""
    return getattr(settings, 'ZIP_IMPORT_MAX_ENTRIES', 5000)


def _get_max_total_bytes() -> int:
    """Get maximum total bytes allowed in a ZIP."""
    return getattr(settings, 'ZIP_IMPORT_MAX_TOTAL_BYTES', 1_000_000_000)


@dataclass(frozen=True)
class ImportResult:
    """Result of a ZIP import operation."""

    collection: Collection
    created_files: int
    skipped_duplicates: int
    total_bytes: int


def classify_extension(ext: str) -> str:
    """
    Classify file extension into VaultFile.FileType values.

    Args:
        ext: File extension (e.g., '.stl', '.pdf')

    Returns:
        One of VaultFile.FileType values (STL, PDF, or OTHER)
    """
    e = ext.lower()
    if e == ".stl":
        return VaultFile.FileType.STL
    if e == ".pdf":
        return VaultFile.FileType.PDF
    return VaultFile.FileType.OTHER


def safe_join(base: Path, target: str) -> Path:
    """
    Prevent zip-slip attacks by ensuring the final path is within base.

    Args:
        base: Base directory path
        target: Target file path from ZIP archive

    Returns:
        Safe resolved path

    Raises:
        ValueError: If the target path would escape the base directory
    """
    dest = (base / target).resolve()
    if not str(dest).startswith(str(base.resolve())):
        raise ValueError(f"Unsafe path detected: {target}")
    return dest


def sha256_bytes(data: bytes) -> str:
    """
    Calculate SHA-256 hash of bytes.

    Args:
        data: Byte data to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data).hexdigest()


@transaction.atomic
def import_zip_as_new_collection(
    zip_path: str,
    *,
    owner: Optional[User] = None
) -> ImportResult:
    """
    Import a ZIP archive as a new collection.

    This function:
    - Validates the archive (no zip-slip, no zip-bomb)
    - Extracts to media/collections/<slug>/
    - Creates a new Collection if not present
    - Creates VaultFile entries (dedupe by sha256 within collection)
    - Emits UserHistory and EmailQueue records
    - Calls RAG indexing for PDFs (if available)

    Args:
        zip_path: Path to the ZIP file to import
        owner: Optional user who is importing the collection

    Returns:
        ImportResult with collection and statistics

    Raises:
        FileNotFoundError: If zip_path does not exist
        ValueError: If ZIP is malformed, too large, or contains unsafe paths
    """
    zip_file = Path(zip_path)
    if not zip_file.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    # Derive collection name from filename
    collection_name = zip_file.stem.replace("_", " ").strip()
    slug = slugify(collection_name) or "collection"

    # Get or create collection
    collection, created = Collection.objects.get_or_create(
        slug=slug,
        defaults={
            "name": collection_name,
            "created_by": owner,
            "source": "zip_import"
        },
    )

    # Set up extraction directory
    media_root = Path(settings.MEDIA_ROOT)
    target_dir = media_root / "collections" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    created_files = 0
    skipped = 0
    total_bytes = 0

    max_entries = _get_max_entries()
    max_total_bytes = _get_max_total_bytes()

    with zipfile.ZipFile(zip_file, "r") as zf:
        # Check for too many entries (zip-bomb protection)
        if len(zf.infolist()) > max_entries:
            raise ValueError(
                f"ZIP too large: {len(zf.infolist())} entries exceeds "
                f"maximum of {max_entries}"
            )

        # Quick total size check to mitigate zip-bombs
        est_total = sum(i.file_size for i in zf.infolist())
        if est_total > max_total_bytes:
            raise ValueError(
                f"ZIP too large: {est_total} bytes exceeds "
                f"maximum of {max_total_bytes}"
            )

        for info in zf.infolist():
            if info.is_dir():
                continue

            # Normalize path and guard against traversal
            dest_rel = Path(info.filename).as_posix()
            dest_path = safe_join(target_dir, dest_rel)

            # Ensure parent dirs exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Read file bytes
            with zf.open(info, "r") as src:
                data = src.read()

            total_bytes += len(data)
            if total_bytes > max_total_bytes:
                raise ValueError(
                    f"ZIP extraction exceeded configured size limit: {total_bytes}"
                )

            # Check for duplicates by hash
            file_hash = sha256_bytes(data)
            if VaultFile.objects.filter(
                collection=collection,
                sha256=file_hash
            ).exists():
                skipped += 1
                continue

            # Write file to disk
            with open(dest_path, "wb") as out:
                out.write(data)

            # Determine file type
            ext = dest_path.suffix.lower()
            ftype = classify_extension(ext)

            # Create VaultFile record
            rel_from_media = dest_path.relative_to(media_root).as_posix()
            VaultFile.objects.create(
                collection=collection,
                file=rel_from_media,
                file_type=ftype,
                sha256=file_hash,
                original_name=Path(info.filename).name,
                size_bytes=len(data),
            )
            created_files += 1

    # Record action in history
    UserHistory.objects.create(
        user=owner,
        action="zip_import",
        metadata={
            "collection": collection.slug,
            "zip": str(zip_file),
            "created_files": created_files,
            "skipped_duplicates": skipped,
            "total_bytes": total_bytes,
        },
    )

    # Queue email notification
    EmailQueue.objects.create(
        to_email=owner.email if owner and owner.email else "admin@example.com",
        subject=f"Imported collection: {collection.name}",
        body=(
            f"Collection '{collection.name}' has been imported.\n"
            f"{created_files} files imported, {skipped} skipped as duplicates.\n"
            f"Total size: {total_bytes} bytes"
        ),
        classification=EmailQueue.Classification.USER_ACTIONS,
    )

    # Enqueue RAG for PDFs (soft-fail if not available)
    try:
        from vault.rag import enqueue_collection_pdfs
        enqueue_collection_pdfs(collection.id)
    except (ImportError, AttributeError):
        # RAG module not yet implemented - continue without it
        pass

    return ImportResult(
        collection=collection,
        created_files=created_files,
        skipped_duplicates=skipped,
        total_bytes=total_bytes
    )
