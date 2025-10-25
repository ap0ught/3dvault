"""Serializers for the vault API."""

from rest_framework import serializers

from vault.models import Collection, VaultFile


class VaultFileSerializer(serializers.ModelSerializer):
    """Serializer for VaultFile model."""

    class Meta:
        model = VaultFile
        fields = [
            'id',
            'collection',
            'file',
            'file_type',
            'sha256',
            'original_name',
            'size_bytes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sha256', 'size_bytes']


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for Collection model."""

    files = VaultFileSerializer(many=True, read_only=True)
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'id',
            'name',
            'slug',
            'source',
            'created_by',
            'created_at',
            'files',
            'file_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def get_file_count(self, obj):
        """Get count of files in collection."""
        return obj.files.count()


class ImportZipSerializer(serializers.Serializer):
    """Serializer for ZIP import request."""

    file = serializers.FileField(required=False, help_text="ZIP file to import")
    zip_path = serializers.CharField(
        required=False,
        help_text="Server path to ZIP file (alternative to file upload)"
    )
    owner_id = serializers.IntegerField(
        required=False,
        help_text="User ID of collection owner"
    )

    def validate(self, data):
        """Ensure either file or zip_path is provided."""
        if not data.get('file') and not data.get('zip_path'):
            raise serializers.ValidationError(
                "Either 'file' or 'zip_path' must be provided"
            )
        if data.get('file') and data.get('zip_path'):
            raise serializers.ValidationError(
                "Only one of 'file' or 'zip_path' should be provided"
            )
        return data


class ImportResultSerializer(serializers.Serializer):
    """Serializer for import result."""

    collection_slug = serializers.CharField()
    collection_name = serializers.CharField()
    created_files = serializers.IntegerField()
    skipped_duplicates = serializers.IntegerField()
    total_bytes = serializers.IntegerField()
