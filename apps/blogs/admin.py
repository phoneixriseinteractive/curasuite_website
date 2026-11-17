"""CuraSuite — Blogs Admin"""
from django.contrib import admin
from .models import Blog, BlogAuthor, BlogCategory, BlogComment, BlogRevision, BlogTag


class BlogRevisionInline(admin.TabularInline):
    model = BlogRevision
    extra = 0
    fields = ["revision_number", "title", "editor", "created_at"]
    readonly_fields = ["revision_number", "title", "editor", "created_at"]
    can_delete = False
    def has_add_permission(self, request, obj=None): return False


@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display  = ["name", "designation", "sort_order", "is_active"]
    search_fields = ["name", "designation"]
    prepopulated_fields = {"slug": ("name",)}
    fields = ["name", "slug", "designation", "bio", "photo", "sort_order", "is_active"]

    def get_queryset(self, request):
        return BlogAuthor.all_objects.all()


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display   = ["title", "author_profile", "category", "status", "is_featured", "reading_time_minutes", "view_count", "published_at"]
    list_filter    = ["status", "is_featured", "category"]
    search_fields  = ["title", "excerpt", "content"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags"]
    readonly_fields   = ["reading_time_minutes", "view_count", "version", "created_at", "updated_at"]
    inlines = [BlogRevisionInline]
    fieldsets = (
        ("Post", {"fields": ("title", "slug", "author", "author_profile", "category", "tags", "is_featured")}),
        ("Content", {"fields": ("excerpt", "content", "featured_image", "featured_image_alt")}),
        ("Publishing", {"fields": ("status", "published_at", "allow_comments", "reading_time_minutes", "view_count", "version")}),
    )


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "sort_order"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display  = ["author_name", "blog", "status", "created_at"]
    list_filter   = ["status"]
    list_editable = ["status"]
    search_fields = ["author_name", "author_email", "content"]
