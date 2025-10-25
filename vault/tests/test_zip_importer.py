"""Tests for ZIP to Collection import functionality."""

import io
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from services.collections.import_zip import (
    classify_extension,
    import_zip_as_new_collection,
    safe_join,
    sha256_bytes,
)
from vault.models import Collection, EmailQueue, UserHistory, VaultFile

User = get_user_model()


class ClassifyExtensionTest(TestCase):
    """Test file extension classification."""

    def test_stl_extension(self):
        """Test STL file classification."""
        self.assertEqual(classify_extension('.stl'), VaultFile.FileType.STL)
        self.assertEqual(classify_extension('.STL'), VaultFile.FileType.STL)

    def test_pdf_extension(self):
        """Test PDF file classification."""
        self.assertEqual(classify_extension('.pdf'), VaultFile.FileType.PDF)
        self.assertEqual(classify_extension('.PDF'), VaultFile.FileType.PDF)

    def test_other_extension(self):
        """Test other file types."""
        self.assertEqual(classify_extension('.txt'), VaultFile.FileType.OTHER)
        self.assertEqual(classify_extension('.jpg'), VaultFile.FileType.OTHER)
        self.assertEqual(classify_extension('.obj'), VaultFile.FileType.OTHER)


class SafeJoinTest(TestCase):
    """Test zip-slip protection."""

    def test_safe_path(self):
        """Test that safe paths work correctly."""
        base = Path("/tmp/base")
        result = safe_join(base, "safe/file.txt")
        self.assertTrue(str(result).startswith(str(base.resolve())))

    def test_unsafe_path_raises_error(self):
        """Test that path traversal attempts raise ValueError."""
        base = Path("/tmp/base")
        with self.assertRaises(ValueError) as ctx:
            safe_join(base, "../../../etc/passwd")
        self.assertIn("Unsafe path", str(ctx.exception))

    def test_absolute_path_raises_error(self):
        """Test that absolute paths raise ValueError."""
        base = Path("/tmp/base")
        with self.assertRaises(ValueError):
            safe_join(base, "/etc/passwd")


class SHA256Test(TestCase):
    """Test SHA-256 hashing."""

    def test_sha256_bytes(self):
        """Test SHA-256 of bytes."""
        data = b"Hello, World!"
        expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        self.assertEqual(sha256_bytes(data), expected)

    def test_empty_bytes(self):
        """Test SHA-256 of empty bytes."""
        data = b""
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(sha256_bytes(data), expected)


def create_test_zip(files: dict) -> str:
    """
    Create a test ZIP file.

    Args:
        files: Dictionary mapping filenames to content (bytes or str)

    Returns:
        Path to the created ZIP file
    """
    tmp = tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False)
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            if isinstance(content, str):
                content = content.encode('utf-8')
            zf.writestr(filename, content)
    tmp.close()
    return tmp.name


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImportZipTest(TestCase):
    """Test ZIP import functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and 'tmp' in str(media_root):
            shutil.rmtree(media_root, ignore_errors=True)

    def test_import_valid_zip(self):
        """Test importing a valid ZIP with STL and PDF files."""
        zip_path = create_test_zip({
            'model.stl': b'STL content here',
            'document.pdf': b'PDF content here',
            'readme.txt': b'Text content here',
        })

        try:
            result = import_zip_as_new_collection(zip_path, owner=self.user)

            # Check result
            self.assertEqual(result.created_files, 3)
            self.assertEqual(result.skipped_duplicates, 0)
            self.assertTrue(result.total_bytes > 0)

            # Check collection was created
            self.assertIsNotNone(result.collection)
            self.assertEqual(result.collection.created_by, self.user)

            # Check files were created
            files = VaultFile.objects.filter(collection=result.collection)
            self.assertEqual(files.count(), 3)

            # Check file types
            stl_files = files.filter(file_type=VaultFile.FileType.STL)
            pdf_files = files.filter(file_type=VaultFile.FileType.PDF)
            other_files = files.filter(file_type=VaultFile.FileType.OTHER)

            self.assertEqual(stl_files.count(), 1)
            self.assertEqual(pdf_files.count(), 1)
            self.assertEqual(other_files.count(), 1)

            # Check history was created
            history = UserHistory.objects.filter(user=self.user, action='zip_import')
            self.assertEqual(history.count(), 1)

            # Check email was queued
            emails = EmailQueue.objects.filter(to_email=self.user.email)
            self.assertEqual(emails.count(), 1)

        finally:
            Path(zip_path).unlink(missing_ok=True)

    def test_import_duplicate_handling(self):
        """Test that re-importing the same files skips duplicates."""
        zip_path = create_test_zip({
            'file1.stl': b'Content 1',
            'file2.pdf': b'Content 2',
        })

        try:
            # First import
            result1 = import_zip_as_new_collection(zip_path, owner=self.user)
            self.assertEqual(result1.created_files, 2)
            self.assertEqual(result1.skipped_duplicates, 0)

            # Second import (same ZIP, same collection name)
            result2 = import_zip_as_new_collection(zip_path, owner=self.user)
            self.assertEqual(result2.created_files, 0)
            self.assertEqual(result2.skipped_duplicates, 2)

            # Should still only have 2 files total
            files = VaultFile.objects.filter(collection=result1.collection)
            self.assertEqual(files.count(), 2)

        finally:
            Path(zip_path).unlink(missing_ok=True)

    def test_zip_slip_protection(self):
        """Test that malicious paths are rejected."""
        zip_path = create_test_zip({
            '../../../etc/passwd': b'malicious content',
        })

        try:
            with self.assertRaises(ValueError) as ctx:
                import_zip_as_new_collection(zip_path, owner=self.user)
            self.assertIn("Unsafe path", str(ctx.exception))

        finally:
            Path(zip_path).unlink(missing_ok=True)

    @override_settings(ZIP_IMPORT_MAX_ENTRIES=2)
    def test_too_many_entries(self):
        """Test that ZIPs with too many entries are rejected."""
        zip_path = create_test_zip({
            f'file{i}.txt': b'content' for i in range(5)
        })

        try:
            with self.assertRaises(ValueError) as ctx:
                import_zip_as_new_collection(zip_path, owner=self.user)
            self.assertIn("entries exceeds", str(ctx.exception))

        finally:
            Path(zip_path).unlink(missing_ok=True)

    @override_settings(ZIP_IMPORT_MAX_TOTAL_BYTES=100)
    def test_size_limit(self):
        """Test that oversized ZIPs are rejected."""
        # Create a file larger than the limit
        large_content = b'X' * 200
        zip_path = create_test_zip({
            'large_file.txt': large_content,
        })

        try:
            with self.assertRaises(ValueError) as ctx:
                import_zip_as_new_collection(zip_path, owner=self.user)
            self.assertIn("exceeds", str(ctx.exception).lower())

        finally:
            Path(zip_path).unlink(missing_ok=True)

    def test_file_not_found(self):
        """Test that missing files raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            import_zip_as_new_collection('/nonexistent/file.zip', owner=self.user)

    @patch('vault.rag.enqueue_collection_pdfs')
    def test_rag_enqueue_called(self, mock_enqueue):
        """Test that RAG indexing is triggered for PDFs."""
        zip_path = create_test_zip({
            'document.pdf': b'PDF content',
        })

        try:
            result = import_zip_as_new_collection(zip_path, owner=self.user)
            mock_enqueue.assert_called_once_with(result.collection.id)

        finally:
            Path(zip_path).unlink(missing_ok=True)

    def test_collection_name_from_zip(self):
        """Test that collection name is derived from ZIP filename."""
        # Create a ZIP with underscores in name
        tmp = tempfile.NamedTemporaryFile(
            mode='wb',
            suffix='.zip',
            prefix='Test_Collection_Name_',
            delete=False
        )
        with zipfile.ZipFile(tmp, 'w') as zf:
            zf.writestr('file.txt', b'content')
        tmp.close()

        try:
            result = import_zip_as_new_collection(tmp.name, owner=self.user)
            # Underscores should be converted to spaces
            self.assertIn('Test', result.collection.name)
            self.assertIn('Collection', result.collection.name)

        finally:
            Path(tmp.name).unlink(missing_ok=True)

    def test_sha256_deduplication(self):
        """Test that files with same content (hash) are deduplicated."""
        content = b'Same content'

        # Create ZIP with two files having identical content
        zip_path = create_test_zip({
            'file1.txt': content,
            'file2.txt': content,
        })

        try:
            result = import_zip_as_new_collection(zip_path, owner=self.user)

            # First file should be created
            self.assertEqual(result.created_files, 1)
            # Second file should be skipped as duplicate
            self.assertEqual(result.skipped_duplicates, 1)

        finally:
            Path(zip_path).unlink(missing_ok=True)
