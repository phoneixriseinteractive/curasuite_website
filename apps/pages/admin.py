"""CuraSuite — Pages Admin"""
from django.contrib import admin
from .models import Page, PageRevision


class PageRevisionInline(admin.TabularInline):
    model = PageRevision
    extra = 0
    fields = ["revision_number", "title", "editor", "created_at"]
    readonly_fields = ["revision_number", "title", "editor", "created_at"]
    can_delete = False
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ["title", "slug", "page_type", "status", "show_in_nav", "version", "updated_at"]
    list_filter   = ["status", "page_type", "template", "show_in_nav"]
    search_fields = ["title", "slug", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["version", "created_at", "updated_at", "published_at"]
    inlines = [PageRevisionInline]

    fieldsets = (
        ("Page", {"fields": ("title", "slug", "page_type", "template", "parent")}),
        ("Content", {"fields": ("excerpt", "content", "featured_image")}),
        ("Settings", {"fields": ("show_in_sitemap", "show_in_nav")}),
        ("Publishing", {"fields": ("status", "published_at", "version", "created_at", "updated_at")}),
    )
