"""CuraSuite — SEO Admin."""
from django.contrib import admin
from .models import Redirect, SEOMetadata


@admin.register(SEOMetadata)
class SEOMetadataAdmin(admin.ModelAdmin):
    list_display  = ["seo_title", "content_type", "schema_type", "robots"]
    list_filter   = ["robots", "schema_type", "content_type"]
    search_fields = ["seo_title", "meta_description", "focus_keyword"]
    fieldsets = (
        ("Core", {"fields": ("content_type", "object_id", "seo_title", "meta_description", "canonical_url", "robots", "focus_keyword")}),
        ("Open Graph", {"fields": ("og_title", "og_description", "og_image"), "classes": ("collapse",)}),
        ("Twitter", {"fields": ("twitter_title", "twitter_description"), "classes": ("collapse",)}),
        ("Schema", {"fields": ("schema_type",), "classes": ("collapse",)}),
    )


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display  = ["old_path", "new_path", "redirect_type", "is_active", "created_at"]
    list_filter   = ["redirect_type", "is_active"]
    search_fields = ["old_path", "new_path", "note"]
    list_editable = ["is_active"]
