"""Admin configuration for vault app."""

import tempfile
from pathlib import Path

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, redirect

from services.collections.import_zip import import_zip_as_new_collection
from vault.models import Collection, EmailQueue, UserHistory, VaultFile


class ZipImportForm(forms.Form):
    """Form for ZIP import admin action."""

    zip_file = forms.FileField(
        label="ZIP File",
        help_text="Select a ZIP file to import as a new collection"
    )
    owner = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Owner",
        help_text="Optional: Select the owner of this collection"
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with user queryset."""
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['owner'].queryset = User.objects.all()


class VaultFileInline(admin.TabularInline):
    """Inline admin for VaultFile."""

    model = VaultFile
    extra = 0
    readonly_fields = ['file_type', 'sha256', 'original_name', 'size_bytes', 'created_at']
    fields = ['original_name', 'file_type', 'size_bytes', 'sha256', 'created_at']
    can_delete = True


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Admin for Collection model."""

    list_display = ['name', 'slug', 'source', 'created_by', 'created_at', 'file_count']
    list_filter = ['source', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['slug', 'created_at']
    inlines = [VaultFileInline]
    actions = ['import_zip_action']

    def file_count(self, obj):
        """Get count of files in collection."""
        return obj.files.count()
    file_count.short_description = 'Files'

    def import_zip_action(self, request, queryset):
        """Admin action to import ZIP as new collection."""
        if 'apply' in request.POST:
            form = ZipImportForm(request.POST, request.FILES)
            if form.is_valid():
                zip_file = form.cleaned_data['zip_file']
                owner = form.cleaned_data.get('owner')

                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix='.zip'
                ) as tmp_file:
                    for chunk in zip_file.chunks():
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name

                try:
                    result = import_zip_as_new_collection(tmp_path, owner=owner)
                    self.message_user(
                        request,
                        f"Successfully imported collection '{result.collection.name}': "
                        f"{result.created_files} files created, "
                        f"{result.skipped_duplicates} duplicates skipped, "
                        f"{result.total_bytes} bytes total",
                        messages.SUCCESS
                    )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Import failed: {str(e)}",
                        messages.ERROR
                    )
                finally:
                    # Clean up temporary file
                    import os
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

                return redirect(request.get_full_path())

        else:
            form = ZipImportForm()

        return render(
            request,
            'admin/vault/import_zip.html',
            {'form': form, 'title': 'Import ZIP as New Collection'}
        )

    import_zip_action.short_description = "Import ZIP as New Collection"


@admin.register(VaultFile)
class VaultFileAdmin(admin.ModelAdmin):
    """Admin for VaultFile model."""

    list_display = ['original_name', 'collection', 'file_type', 'size_bytes', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['original_name', 'sha256']
    readonly_fields = ['sha256', 'size_bytes', 'created_at']


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    """Admin for UserHistory model."""

    list_display = ['user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'action']
    readonly_fields = ['user', 'action', 'metadata', 'created_at']

    def has_add_permission(self, request):
        """Disable manual creation of history entries."""
        return False


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    """Admin for EmailQueue model."""

    list_display = ['to_email', 'subject', 'classification', 'is_sent', 'created_at']
    list_filter = ['classification', 'is_sent', 'created_at']
    search_fields = ['to_email', 'subject']
    readonly_fields = ['created_at']
    actions = ['mark_as_sent']

    def mark_as_sent(self, request, queryset):
        """Mark selected emails as sent."""
        count = queryset.update(is_sent=True)
        self.message_user(
            request,
            f"{count} email(s) marked as sent",
            messages.SUCCESS
        )
    mark_as_sent.short_description = "Mark selected emails as sent"

