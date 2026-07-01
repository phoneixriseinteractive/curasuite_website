"""CuraSuite — Products Admin."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Product, ProductFAQ, ProductFeature,
    ProductIntegration, ProductPricing, ProductScreenshot,
)


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1
    fields = ["title", "description", "icon_name", "is_highlighted", "sort_order"]
    ordering = ["sort_order"]


class ProductPricingInline(admin.TabularInline):
    model = ProductPricing
    extra = 1
    fields = ["tier_name", "price", "billing_cycle", "is_featured", "cta_text", "sort_order"]
    ordering = ["sort_order"]


class ProductFAQInline(admin.TabularInline):
    model = ProductFAQ
    extra = 1
    fields = ["question", "answer", "sort_order"]
    ordering = ["sort_order"]


class ProductScreenshotInline(admin.TabularInline):
    model = ProductScreenshot
    extra = 1
    fields = ["title", "image", "alt_text", "caption", "sort_order"]
    ordering = ["sort_order"]


class ProductIntegrationInline(admin.TabularInline):
    model = ProductIntegration
    extra = 1
    fields = ["name", "logo", "url", "sort_order"]
    ordering = ["sort_order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ["name", "key", "status", "sort_order", "color_preview", "published_at"]
    list_filter   = ["status", "key"]
    search_fields = ["name", "short_description", "tagline"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "published_at", "published_by"]
    ordering = ["sort_order"]

    fieldsets = (
        ("Identity", {
            "fields": ("key", "name", "slug", "tagline", "color", "sort_order"),
        }),
        ("Content", {
            "fields": ("short_description", "long_description", "target_audience"),
        }),
        ("Visuals", {
            "fields": ("icon", "hero_image"),
            "classes": ("collapse",),
        }),
        ("Publishing", {
            "fields": ("status", "published_at", "published_by", "created_at", "updated_at"),
        }),
    )

    inlines = [
        ProductFeatureInline,
        ProductPricingInline,
        ProductFAQInline,
        ProductScreenshotInline,
        ProductIntegrationInline,
    ]

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:4px;border:1px solid #ccc;"></span> {}',
            obj.color, obj.color,
        )
    color_preview.short_description = "Color"
