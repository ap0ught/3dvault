"""API views for the vault app."""

import os
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from services.collections.import_zip import import_zip_as_new_collection
from vault.models import Collection, VaultFile
from vault.serializers import (
    CollectionSerializer,
    ImportResultSerializer,
    ImportZipSerializer,
    VaultFileSerializer,
)

User = get_user_model()


class CollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Collection model."""

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['post'], url_path='import-zip')
    def import_zip(self, request):
        """
        Import a ZIP file as a new collection.

        Accepts either:
        - Multipart form data with 'file' field containing ZIP
        - JSON with 'zip_path' pointing to server file path

        Optional 'owner_id' field specifies the collection owner.
        """
        serializer = ImportZipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        owner_id = data.get('owner_id')
        owner = None

        if owner_id:
            try:
                owner = User.objects.get(pk=owner_id)
            except User.DoesNotExist:
                return Response(
                    {'error': f'User with ID {owner_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Handle file upload or server path
        if 'file' in data:
            # Save uploaded file to temporary location
            uploaded_file = data['file']
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.zip'
            ) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            try:
                result = import_zip_as_new_collection(tmp_path, owner=owner)
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            # Use server path
            zip_path = data['zip_path']
            if not Path(zip_path).exists():
                return Response(
                    {'error': f'File not found: {zip_path}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            result = import_zip_as_new_collection(zip_path, owner=owner)

        # Prepare response
        result_data = {
            'collection_slug': result.collection.slug,
            'collection_name': result.collection.name,
            'created_files': result.created_files,
            'skipped_duplicates': result.skipped_duplicates,
            'total_bytes': result.total_bytes,
        }

        result_serializer = ImportResultSerializer(data=result_data)
        result_serializer.is_valid()

        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED
        )


class VaultFileViewSet(viewsets.ModelViewSet):
    """ViewSet for VaultFile model."""

    queryset = VaultFile.objects.all()
    serializer_class = VaultFileSerializer

