"""CuraSuite — Newsletter Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import NewsletterCampaign, NewsletterSend, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display  = ["email", "first_name", "status_badge", "source", "confirmed_at", "created_at"]
    list_filter   = ["status", "source"]
    search_fields = ["email", "first_name"]
    readonly_fields = ["confirmation_token", "unsubscribe_token", "confirmation_sent_at",
                       "confirmed_at", "unsubscribed_at", "created_at", "updated_at"]
    actions = ["mark_confirmed", "mark_unsubscribed"]

    def status_badge(self, obj):
        colors = {"confirmed": "#10B981", "pending": "#F59E0B",
                  "unsubscribed": "#6B7280", "bounced": "#EF4444"}
        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def mark_confirmed(self, request, queryset):
        for sub in queryset:
            sub.confirm()
        self.message_user(request, f"{queryset.count()} subscribers confirmed.")
    mark_confirmed.short_description = "Mark selected as confirmed"

    def mark_unsubscribed(self, request, queryset):
        for sub in queryset:
            sub.unsubscribe(reason="Admin action")
        self.message_user(request, f"{queryset.count()} subscribers unsubscribed.")
    mark_unsubscribed.short_description = "Mark selected as unsubscribed"


class NewsletterSendInline(admin.TabularInline):
    model = NewsletterSend
    extra = 0
    fields = ["subscriber", "status", "sent_at", "opened_at", "clicked_at"]
    readonly_fields = ["subscriber", "sent_at", "opened_at", "clicked_at"]
    can_delete = False
    max_num = 20
    def has_add_permission(self, request, obj=None): return False


@admin.register(NewsletterCampaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display  = ["subject", "status", "total_sent", "open_rate", "click_rate", "sent_at"]
    list_filter   = ["status"]
    search_fields = ["subject"]
    readonly_fields = ["total_sent", "total_opens", "total_clicks",
                       "total_bounces", "total_unsubs", "sent_at", "created_at"]
    inlines = [NewsletterSendInline]
    fieldsets = (
        ("Campaign", {"fields": ("subject", "preview_text", "content_html", "content_text")}),
        ("Schedule", {"fields": ("status", "scheduled_at", "sent_at")}),
        ("Stats", {"fields": ("total_sent", "total_opens", "total_clicks", "total_bounces", "total_unsubs"), "classes": ("collapse",)}),
    )
