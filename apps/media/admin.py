"""CuraSuite — Media Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile, MediaFolder


@admin.register(MediaFolder)
class MediaFolderAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "created_at"]
    search_fields = ["name"]


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display  = ["preview", "title", "file_type", "file_size_display", "folder", "uploaded_by", "created_at"]
    list_filter   = ["file_type", "folder"]
    search_fields = ["original_name", "title", "alt_text", "tags"]
    readonly_fields = ["original_name", "mime_type", "file_type", "file_size",
                       "width", "height", "created_at", "updated_at", "preview"]

    def preview(self, obj):
        if obj.is_image and obj.file:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.file.url)
        return obj.file_type
    preview.short_description = "Preview"
