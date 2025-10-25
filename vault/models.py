"""Models for the 3D Vault application."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Collection(models.Model):
    """A collection of 3D files and related resources."""

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    source = models.CharField(max_length=64, default="manual_upload")
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="collections_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VaultFile(models.Model):
    """A file within a collection."""

    class FileType(models.TextChoices):
        STL = "stl", "STL"
        PDF = "pdf", "PDF"
        OTHER = "other", "Other"

    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to="collections/%Y/%m/%d/")
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        default=FileType.OTHER
    )
    sha256 = models.CharField(max_length=64, db_index=True)
    original_name = models.CharField(max_length=512)
    size_bytes = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['collection', 'sha256']),
        ]

    def __str__(self) -> str:
        return f"{self.original_name} ({self.file_type})"


class UserHistory(models.Model):
    """Audit log of user actions."""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=128)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "User histories"

    def __str__(self) -> str:
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.action} - {self.created_at}"


class EmailQueue(models.Model):
    """Queue for outgoing emails."""

    class Classification(models.TextChoices):
        ADMINISTRATIVE = "administrative", "Administrative"
        FILE_UPDATES = "file_updates", "File Updates"
        USER_ACTIONS = "user_actions", "User Actions"

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    classification = models.CharField(
        max_length=32,
        choices=Classification.choices,
        default=Classification.USER_ACTIONS
    )
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        status = "Sent" if self.is_sent else "Pending"
        return f"{self.to_email} - {self.subject} ({status})"

