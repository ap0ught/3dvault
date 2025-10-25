"""Tests for the ZIP import API endpoint."""

import tempfile
import zipfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from vault.models import Collection, VaultFile

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImportZipAPITest(TestCase):
    """Test the ZIP import API endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Authenticate the client
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        """Clean up test files."""
        import shutil
        from django.conf import settings
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and 'tmp' in str(media_root):
            shutil.rmtree(media_root, ignore_errors=True)

    def test_import_zip_with_file_upload(self):
        """Test importing a ZIP via file upload."""
        # Create a test ZIP in memory
        zip_buffer = tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False)
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('model.stl', b'STL content')
            zf.writestr('doc.pdf', b'PDF content')
        zip_buffer.close()

        try:
            # Read the ZIP file
            with open(zip_buffer.name, 'rb') as f:
                zip_content = f.read()

            # Create an uploaded file
            uploaded_file = SimpleUploadedFile(
                'test_collection.zip',
                zip_content,
                content_type='application/zip'
            )

            # Make the API request
            response = self.client.post(
                '/api/collections/import-zip/',
                {'file': uploaded_file, 'owner_id': self.user.id},
                format='multipart'
            )

            # Check response
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn('collection_slug', response.data)
            self.assertIn('created_files', response.data)
            self.assertEqual(response.data['created_files'], 2)

            # Verify collection was created
            collection = Collection.objects.get(slug=response.data['collection_slug'])
            self.assertEqual(collection.files.count(), 2)

        finally:
            Path(zip_buffer.name).unlink(missing_ok=True)

    def test_import_zip_with_server_path(self):
        """Test importing a ZIP via server path."""
        # Create a test ZIP
        zip_path = tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('file.txt', b'content')
        zip_path.close()

        try:
            # Make the API request
            response = self.client.post(
                '/api/collections/import-zip/',
                {
                    'zip_path': zip_path.name,
                    'owner_id': self.user.id
                },
                format='json'
            )

            # Check response
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['created_files'], 1)

        finally:
            Path(zip_path.name).unlink(missing_ok=True)

    def test_import_zip_invalid_user(self):
        """Test that invalid user ID returns error."""
        zip_path = tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('file.txt', b'content')
        zip_path.close()

        try:
            response = self.client.post(
                '/api/collections/import-zip/',
                {
                    'zip_path': zip_path.name,
                    'owner_id': 99999  # Non-existent user
                },
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)

        finally:
            Path(zip_path.name).unlink(missing_ok=True)

    def test_import_zip_missing_parameters(self):
        """Test that missing file and path returns error."""
        response = self.client.post(
            '/api/collections/import-zip/',
            {'owner_id': self.user.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_zip_nonexistent_path(self):
        """Test that nonexistent path returns error."""
        response = self.client.post(
            '/api/collections/import-zip/',
            {
                'zip_path': '/nonexistent/path.zip',
                'owner_id': self.user.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
