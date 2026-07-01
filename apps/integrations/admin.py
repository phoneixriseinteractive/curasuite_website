"""CuraSuite — Integrations Admin"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Integration, SiteSettings


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display  = ["provider_display", "is_enabled", "status_badge", "last_tested_at"]
    list_filter   = ["is_enabled", "last_test_status"]
    readonly_fields = ["last_tested_at", "last_test_status", "last_test_message", "created_at", "updated_at"]
    fieldsets = (
        ("Integration", {"fields": ("provider", "is_enabled")}),
        ("Configuration", {"fields": ("config",), "description": "Non-secret config only. Store API keys in environment variables."}),
        ("Test Results", {"fields": ("last_tested_at", "last_test_status", "last_test_message"), "classes": ("collapse",)}),
    )

    def provider_display(self, obj):
        return obj.get_provider_display()
    provider_display.short_description = "Provider"

    def status_badge(self, obj):
        if not obj.last_test_status:
            return format_html('<span style="color:var(--text-muted,#9CA3AF);">Not tested</span>')
        color = "#10B981" if obj.last_test_status == "ok" else "#EF4444"
        label = "OK" if obj.last_test_status == "ok" else "Error"
        return format_html('<span style="color:{};">{}</span>', color, label)
    status_badge.short_description = "Last test"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Analytics", {
            "fields": ("ga4_measurement_id", "gtm_container_id", "meta_pixel_id", "clarity_project_id"),
        }),
        ("WhatsApp Widget", {
            "fields": ("whatsapp_enabled", "whatsapp_phone", "whatsapp_message", "whatsapp_tooltip"),
        }),
        ("AI Chatbot", {
            "fields": ("chatbot_enabled", "chatbot_name", "chatbot_greeting", "chatbot_system_prompt"),
        }),
        ("CAPTCHA", {
            "fields": ("captcha_enabled", "captcha_provider", "captcha_site_key"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
