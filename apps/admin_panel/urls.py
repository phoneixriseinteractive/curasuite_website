"""CuraSuite — Admin Panel URLs"""
from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    # Auth
    path("login/",  views.admin_login,  name="login"),
    path("logout/", views.admin_logout, name="logout"),

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

    # Settings
    path("settings/",              views.site_settings,      name="settings"),
    path("settings/advanced/",     views.advanced_settings,  name="advanced_settings"),
]
