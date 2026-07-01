"""CuraSuite — CRM Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import DemoRequest, Lead, LeadActivity, LeadNote


class LeadNoteInline(admin.TabularInline):
    model   = LeadNote
    extra   = 1
    fields  = ["content", "author", "created_at"]
    readonly_fields = ["created_at"]


class LeadActivityInline(admin.TabularInline):
    model   = LeadActivity
    extra   = 0
    fields  = ["activity_type", "description", "performed_by", "created_at"]
    readonly_fields = ["created_at"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class DemoRequestInline(admin.TabularInline):
    model  = DemoRequest
    extra  = 0
    fields = ["product_interest", "preferred_date", "preferred_time", "status", "handled_by"]
    readonly_fields = ["created_at"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "email", "phone", "status_badge", "source", "product_interest", "score", "created_at"]
    list_filter   = ["status", "source", "business_type", "product_interest"]
    search_fields = ["full_name", "email", "organization", "city"]
    readonly_fields = ["created_at", "updated_at"]
    list_editable  = ["score"]
    date_hierarchy = "created_at"
    inlines        = [DemoRequestInline, LeadNoteInline, LeadActivityInline]

    fieldsets = (
        ("Contact", {"fields": ("full_name", "email", "phone", "organization", "city", "message")}),
        ("Classification", {"fields": ("business_type", "product_interest", "status", "score", "assigned_to")}),
        ("Attribution", {"fields": ("source", "utm_source", "utm_medium", "utm_campaign", "utm_content", "referrer_url"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        colors = {
            "new": "#3B82F6", "contacted": "#F59E0B", "qualified": "#8B5CF6",
            "demo_scheduled": "#06B6D4", "won": "#10B981", "lost": "#EF4444",
        }
        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display  = ["lead", "product_interest", "preferred_date", "preferred_time", "status", "created_at"]
    list_filter   = ["status", "product_interest"]
    search_fields = ["lead__full_name", "lead__email"]
    readonly_fields = ["created_at"]
