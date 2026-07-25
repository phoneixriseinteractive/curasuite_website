"""CuraSuite — Admin Panel URLs"""
from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    PasswordResetCompleteView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetView,
)

from . import views
from .forms import AdminPasswordResetForm

app_name = "admin_panel"

urlpatterns = [
    # Auth
    path("login/",              views.admin_login,      name="login"),
    path("login/otp/",          views.admin_otp_verify,  name="otp_verify"),
    path("login/otp/resend/",   views.admin_otp_resend,  name="otp_resend"),
    path("logout/",              views.admin_logout,     name="logout"),

    # Password reset
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="admin_panel/auth/password_reset.html",
            email_template_name="admin_panel/auth/emails/password_reset_email.txt",
            subject_template_name="admin_panel/auth/emails/password_reset_subject.txt",
            form_class=AdminPasswordResetForm,
            success_url=reverse_lazy("admin_panel:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="admin_panel/auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="admin_panel/auth/password_reset_confirm.html",
            success_url=reverse_lazy("admin_panel:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(template_name="admin_panel/auth/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # CRM
    path("crm/leads/",              views.crm_leads,       name="crm_leads"),
    path("crm/leads/create/",       views.crm_lead_create, name="crm_lead_create"),
    path("crm/leads/<uuid:pk>/",    views.crm_lead_detail, name="crm_lead_detail"),

    # Pages
    path("pages/",                  views.pages_list,  name="pages_list"),
    path("pages/create/",           views.page_create, name="page_create"),
    path("pages/<uuid:pk>/edit/",   views.page_edit,   name="page_edit"),
    path("pages/<uuid:pk>/delete/", views.page_delete, name="page_delete"),

    # Blogs
    path("blogs/",                        views.blogs_list,      name="blogs_list"),
    path("blogs/create/",                 views.blog_create,     name="blog_create"),
    path("blogs/<uuid:pk>/edit/",         views.blog_edit,       name="blog_edit"),
    path("blogs/<uuid:pk>/delete/",       views.blog_delete,     name="blog_delete"),
    path("blogs/categories/",             views.blog_categories, name="blog_categories"),
    path("blogs/comments/",               views.blog_comments,   name="blog_comments"),

    # Products
    path("products/",                     views.products_list,  name="products_list"),
    path("products/create/",              views.product_create, name="product_create"),
    path("products/<uuid:pk>/edit/",      views.product_edit,   name="product_edit"),

    # Newsletter
    path("newsletter/",                          views.newsletter_subscribers,     name="newsletter"),
    path("newsletter/campaigns/",                views.newsletter_campaigns,       name="newsletter_campaigns"),
    path("newsletter/campaigns/create/",         views.newsletter_campaign_create, name="newsletter_campaign_create"),
    path("newsletter/campaigns/<uuid:pk>/edit/", views.newsletter_campaign_edit,   name="newsletter_campaign_edit"),

    # Media
    path("media/",                 views.media_library, name="media_library"),
    path("media/upload/",          views.media_upload,  name="media_upload"),
    path("media/<uuid:pk>/delete/",views.media_delete,  name="media_delete"),

    # FAQs
    path("faqs/",                  views.faqs_list, name="faqs_list"),
    path("faqs/<uuid:pk>/edit/",   views.faq_edit,  name="faq_edit"),

    # Testimonials
    path("testimonials/",                  views.testimonials_list,   name="testimonials_list"),
    path("testimonials/create/",           views.testimonial_create,  name="testimonial_create"),
    path("testimonials/<uuid:pk>/edit/",   views.testimonial_edit,    name="testimonial_edit"),

    # Users
    path("users/",                 views.users_list,  name="users_list"),
    path("users/create/",          views.user_create, name="user_create"),
    path("users/<uuid:pk>/edit/",  views.user_edit,   name="user_edit"),

    # Audit
    path("audit/",                 views.audit_logs, name="audit_logs"),

    # Pricing Manager
    path("pricing/",                              views.pricing_list,   name="pricing_list"),
    path("pricing/<uuid:product_pk>/create/",     views.pricing_create, name="pricing_create"),
    path("pricing/<uuid:pk>/edit/",               views.pricing_edit,   name="pricing_edit"),

    # Landing Pages
    path("landing-pages/",                views.landing_pages_list,  name="landing_pages_list"),
    path("landing-pages/create/",         views.landing_page_create, name="landing_page_create"),
    path("landing-pages/<uuid:pk>/edit/", views.landing_page_edit,   name="landing_page_edit"),

    # Settings
    path("settings/",              views.site_settings,      name="settings"),
    path("settings/advanced/",     views.advanced_settings,  name="advanced_settings"),
]
