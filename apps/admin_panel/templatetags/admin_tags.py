"""CuraSuite — Admin Panel Template Tags"""
from django import template
register = template.Library()

STATUS_BADGE_MAP = {
    # Lead statuses
    "new":            "blue",
    "contacted":      "amber",
    "qualified":      "amber",
    "demo_scheduled": "amber",
    "proposal_sent":  "default",
    "negotiation":    "default",
    "won":            "green",
    "lost":           "red",
    "unqualified":    "default",
    # Newsletter
    "confirmed":      "green",
    "pending":        "amber",
    "unsubscribed":   "default",
    "bounced":        "red",
    # Blog / Page
    "published":      "green",
    "draft":          "default",
    "review":         "amber",
    "archived":       "default",
    # Demo
    "confirmed":      "green",
    "completed":      "green",
    "cancelled":      "red",
    "no_show":        "red",
}

@register.inclusion_tag("admin_panel/components/badge.html")
def status_badge(status, label=None):
    color = STATUS_BADGE_MAP.get(status, "default")
    return {"color": color, "label": label or status.replace("_", " ").title()}
