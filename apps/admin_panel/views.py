"""
CuraSuite — Admin Panel Views
Full CRUD for: Pages, Blogs, CRM, Products, Newsletter, Media, Settings
"""
import json
import logging
import os
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages

from .decorators import admin_required
from .forms import AdminLoginForm
from .selectors import (
    get_dashboard_stats, get_leads_by_source, get_leads_by_status,
    get_recent_demo_requests, get_recent_leads,
)

logger = logging.getLogger(__name__)

def _save_seo(obj, post_data):
    """Save SEO metadata for any model instance from POST data."""
    from apps.seo.services import upsert_seo_metadata
    seo_fields = {}
    for field in ["seo_title","meta_description","focus_keyword","canonical_url",
                  "schema_type","robots","og_title","og_description"]:
        val = post_data.get(field,"").strip()
        if val:
            seo_fields[field] = val
    if seo_fields:
        upsert_seo_metadata(obj, **seo_fields)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _htmx(request):
    return request.headers.get("HX-Request") == "true"

def _toast(request, message, kind="success"):
    """Add a toast message to session for next render."""
    messages.success(request, message) if kind == "success" else messages.error(request, message)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_panel:dashboard")
    error = None
    form  = AdminLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user and user.is_staff:
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            return redirect(request.GET.get("next", "/manage/"))
        error = "Invalid credentials or insufficient permissions."
    return render(request, "admin_panel/auth/login.html", {"form": form, "error": error})


def admin_logout(request):
    logout(request)
    return redirect("admin_panel:login")


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def dashboard(request):
    return render(request, "admin_panel/dashboard/index.html", {
        "stats":     get_dashboard_stats(),
        "leads":     get_recent_leads(),
        "demos":     get_recent_demo_requests(),
        "by_status": get_leads_by_status(),
        "by_source": get_leads_by_source(),
        "page_title": "Dashboard",
        "active_nav": "dashboard",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# CRM
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def crm_leads(request):
    from apps.crm.models import Lead
    qs = Lead.objects.select_related("assigned_to").order_by("-created_at")
    status = request.GET.get("status", "")
    search = request.GET.get("q", "").strip()
    if status: qs = qs.filter(status=status)
    if search: qs = qs.filter(full_name__icontains=search) | qs.filter(email__icontains=search)
    page = Paginator(qs, 20).get_page(request.GET.get("page", 1))
    return render(request, "admin_panel/crm/leads.html", {
        "leads": page, "status_filter": status, "search": search,
        "lead_statuses": Lead.Status.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Leads", "active_nav": "crm",
    })


@admin_required
def crm_lead_detail(request, pk):
    from apps.crm.models import Lead
    from apps.crm.selectors import get_lead_with_history
    from apps.accounts.models import User
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_status":
            lead.status = request.POST.get("status", lead.status)
            lead.score  = request.POST.get("score", lead.score)
            lead.save(update_fields=["status", "score", "updated_at"])
            if _htmx(request):
                return render(request, "admin_panel/crm/partials/lead_status.html", {"lead": lead})
            _toast(request, "Lead updated.")
        elif action == "add_note":
            from apps.crm.models import LeadNote, LeadActivity
            content = request.POST.get("content", "").strip()
            if content:
                from apps.crm.models import LeadNote
                note = lead.notes.create(content=content, author=request.user)
                lead.activities.create(
                    activity_type="note_added",
                    description=content[:100],
                    performed_by=request.user,
                )
                if _htmx(request):
                    return render(request, "admin_panel/crm/partials/note_item.html", {"note": note})
        elif action == "assign":
            uid = request.POST.get("assigned_to")
            if uid:
                try:
                    lead.assigned_to = User.objects.get(pk=uid, is_staff=True)
                    lead.save(update_fields=["assigned_to", "updated_at"])
                    _toast(request, "Lead assigned.")
                except User.DoesNotExist:
                    pass
        return redirect("admin_panel:crm_lead_detail", pk=pk)

    staff = User.objects.filter(is_staff=True).order_by("first_name")
    lead  = get_lead_with_history(pk)
    return render(request, "admin_panel/crm/lead_detail.html", {
        "lead": lead, "staff": staff,
        "lead_statuses": lead.Status.choices,
        "stats": get_dashboard_stats(),
        "page_title": lead.full_name, "active_nav": "crm",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def pages_list(request):
    from apps.pages.models import Page
    pages = Page.all_objects.filter(deleted_at__isnull=True).order_by("slug")
    return render(request, "admin_panel/pages/list.html", {
        "pages": pages,
        "stats": get_dashboard_stats(),
        "page_title": "Pages", "active_nav": "pages",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def page_create(request):
    from apps.pages.models import Page
    from apps.pages.services import create_page
    if request.method == "POST":
        title    = request.POST.get("title", "").strip()
        content  = request.POST.get("content", "")
        excerpt  = request.POST.get("excerpt", "")
        pg_type  = request.POST.get("page_type", "custom")
        template = request.POST.get("template", "default")
        show_nav = "show_in_nav" in request.POST
        show_map = "show_in_sitemap" in request.POST
        if title:
            page = create_page(title=title, content=content, excerpt=excerpt,
                               page_type=pg_type, created_by=request.user)
            page.template = template
            page.show_in_nav = show_nav
            page.show_in_sitemap = show_map
            page.save()
            _save_seo(page, request.POST)
            _toast(request, f'Page "{title}" created.')
            return redirect("admin_panel:page_edit", pk=page.pk)
    return render(request, "admin_panel/pages/form.html", {
        "action": "Create", "page_obj": None, "seo": None,
        "page_types": Page.PageType.choices,
        "templates":  Page.Template.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Create Page", "active_nav": "pages",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def page_edit(request, pk):
    from apps.pages.models import Page
    from apps.pages.services import update_page
    page = get_object_or_404(Page.all_objects, pk=pk, deleted_at__isnull=True)
    if request.method == "POST":
        action = request.POST.get("action", "save")
        update_page(page,
                    title=request.POST.get("title", page.title),
                    content=request.POST.get("content", page.content),
                    updated_by=request.user,
                    excerpt=request.POST.get("excerpt", page.excerpt),
                    template=request.POST.get("template", page.template),
                    show_in_nav="show_in_nav" in request.POST,
                    show_in_sitemap="show_in_sitemap" in request.POST)
        if action == "publish":
            page.publish(published_by=request.user)
            _toast(request, f'Page "{page.title}" published.')
        elif action == "unpublish":
            page.unpublish()
            _toast(request, "Page moved back to draft.")
        else:
            _toast(request, "Changes saved.")
        return redirect("admin_panel:page_edit", pk=pk)

    from apps.seo.selectors import get_seo_for_object
    seo = get_seo_for_object(page) if page else None
    return render(request, "admin_panel/pages/form.html", {
        "action": "Edit", "page_obj": page, "seo": seo,
        "page_types": page.PageType.choices,
        "templates":  page.Template.choices,
        "stats": get_dashboard_stats(),
        "page_title": f"Edit — {page.title}", "active_nav": "pages",
    })


@admin_required
@require_POST
def page_delete(request, pk):
    from apps.pages.models import Page
    page = get_object_or_404(Page.all_objects, pk=pk)
    title = page.title
    page.soft_delete()
    _toast(request, f'Page "{title}" deleted.')
    return redirect("admin_panel:pages_list")


# ═══════════════════════════════════════════════════════════════════════════════
# BLOGS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def blogs_list(request):
    from apps.blogs.models import Blog, BlogCategory
    qs = Blog.all_objects.filter(deleted_at__isnull=True).select_related("author","category").order_by("-created_at")
    if request.GET.get("status"): qs = qs.filter(status=request.GET["status"])
    if request.GET.get("q"):      qs = qs.filter(title__icontains=request.GET["q"])
    page = Paginator(qs, 20).get_page(request.GET.get("page", 1))
    return render(request, "admin_panel/blogs/list.html", {
        "blogs": page,
        "categories": BlogCategory.all_objects.filter(deleted_at__isnull=True),
        "status_filter": request.GET.get("status",""),
        "search": request.GET.get("q",""),
        "stats": get_dashboard_stats(),
        "page_title": "Blog Posts", "active_nav": "blogs",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def blog_create(request):
    from apps.blogs.models import Blog, BlogCategory, BlogTag
    from apps.blogs.services import create_blog
    if request.method == "POST":
        title    = request.POST.get("title","").strip()
        content  = request.POST.get("content","")
        excerpt  = request.POST.get("excerpt","").strip()
        cat_id   = request.POST.get("category")
        tag_ids  = request.POST.getlist("tags")
        featured = "is_featured" in request.POST
        if title:
            from apps.blogs.models import BlogCategory
            cat = BlogCategory.all_objects.filter(pk=cat_id).first() if cat_id else None
            blog = create_blog(title=title, content=content, excerpt=excerpt,
                               category=cat, created_by=request.user)
            blog.is_featured = featured
            if tag_ids:
                blog.tags.set(BlogTag.objects.filter(pk__in=tag_ids))
            blog.save()
            _save_seo(blog, request.POST)
            _toast(request, f'Post "{title}" created.')
            return redirect("admin_panel:blog_edit", pk=blog.pk)
    categories = BlogCategory.all_objects.filter(deleted_at__isnull=True)
    tags       = BlogTag.objects.all()
    return render(request, "admin_panel/blogs/form.html", {
        "action": "Create", "blog_obj": None, "seo": None,
        "categories": categories, "tags": tags,
        "stats": get_dashboard_stats(),
        "page_title": "New Blog Post", "active_nav": "blogs",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def blog_edit(request, pk):
    from apps.blogs.models import Blog, BlogCategory, BlogTag
    from apps.blogs.services import update_blog
    blog = get_object_or_404(Blog.all_objects, pk=pk, deleted_at__isnull=True)
    if request.method == "POST":
        action  = request.POST.get("action","save")
        cat_id  = request.POST.get("category")
        tag_ids = request.POST.getlist("tags")
        cat = BlogCategory.all_objects.filter(pk=cat_id).first() if cat_id else None
        update_blog(blog, updated_by=request.user,
                    title=request.POST.get("title", blog.title),
                    content=request.POST.get("content", blog.content),
                    excerpt=request.POST.get("excerpt", blog.excerpt),
                    category=cat,
                    is_featured="is_featured" in request.POST)
        if tag_ids:
            blog.tags.set(BlogTag.objects.filter(pk__in=tag_ids))
        if action == "publish":
            blog.publish(published_by=request.user)
            _toast(request, f'"{blog.title}" published.')
        elif action == "unpublish":
            blog.unpublish()
            _toast(request, "Post moved to draft.")
        else:
            _toast(request, "Changes saved.")
        return redirect("admin_panel:blog_edit", pk=pk)

    categories = BlogCategory.all_objects.filter(deleted_at__isnull=True)
    tags       = BlogTag.objects.all()
    from apps.seo.selectors import get_seo_for_object
    seo = get_seo_for_object(blog) if blog else None
    return render(request, "admin_panel/blogs/form.html", {
        "action": "Edit", "blog_obj": blog, "seo": seo,
        "categories": categories, "tags": tags,
        "selected_tags": list(blog.tags.values_list("pk", flat=True)),
        "stats": get_dashboard_stats(),
        "page_title": f"Edit — {blog.title}", "active_nav": "blogs",
    })


@admin_required
@require_POST
def blog_delete(request, pk):
    from apps.blogs.models import Blog
    blog = get_object_or_404(Blog.all_objects, pk=pk)
    title = blog.title
    blog.soft_delete()
    _toast(request, f'"{title}" deleted.')
    return redirect("admin_panel:blogs_list")


@admin_required
@require_http_methods(["GET", "POST"])
def blog_categories(request):
    from apps.blogs.models import BlogCategory
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            name = request.POST.get("name","").strip()
            if name:
                BlogCategory.all_objects.create(name=name, created_by=request.user)
                _toast(request, f'Category "{name}" created.')
        elif action == "delete":
            pk = request.POST.get("pk")
            if pk:
                BlogCategory.all_objects.filter(pk=pk).update(is_active=False)
                _toast(request, "Category deleted.")
        elif action == "create_tag":
            from apps.blogs.models import BlogTag
            name = request.POST.get("tag_name","").strip()
            if name:
                BlogTag.objects.get_or_create(name=name)
                _toast(request, f'Tag "{name}" created.')
        elif action == "delete_tag":
            from apps.blogs.models import BlogTag
            BlogTag.objects.filter(pk=request.POST.get("tag_pk")).delete()
            _toast(request, "Tag deleted.")
        return redirect("admin_panel:blog_categories")
    from apps.blogs.models import BlogTag
    cats = BlogCategory.all_objects.filter(deleted_at__isnull=True).order_by("name")
    tags = BlogTag.objects.order_by("name")
    return render(request, "admin_panel/blogs/categories.html", {
        "tags": tags,
        "categories": cats,
        "stats": get_dashboard_stats(),
        "page_title": "Categories & Tags", "active_nav": "blogs",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def products_list(request):
    from apps.products.models import Product
    products = Product.all_objects.filter(deleted_at__isnull=True).order_by("sort_order")
    return render(request, "admin_panel/products/list.html", {
        "products": products,
        "stats": get_dashboard_stats(),
        "page_title": "Products", "active_nav": "products",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk):
    from apps.products.models import Product, ProductFeature, ProductPricing, ProductFAQ
    product = get_object_or_404(Product.all_objects, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        if action == "save_details":
            product.name             = request.POST.get("name", product.name)
            product.tagline          = request.POST.get("tagline", product.tagline)
            product.short_description= request.POST.get("short_description", product.short_description)
            product.long_description = request.POST.get("long_description", product.long_description)
            product.target_audience  = request.POST.get("target_audience", product.target_audience)
            product.color            = request.POST.get("color", product.color)
            product.demo_url         = request.POST.get("demo_url", product.demo_url)
            if "icon" in request.FILES:
                product.icon = request.FILES["icon"]
            if "hero_image" in request.FILES:
                product.hero_image = request.FILES["hero_image"]
            product.save()
            _toast(request, "Product details saved.")

        elif action == "add_feature":
            ProductFeature.objects.create(
                product=product,
                title=request.POST.get("feat_title",""),
                description=request.POST.get("feat_description",""),
                icon_name=request.POST.get("feat_icon",""),
                is_highlighted="feat_highlighted" in request.POST,
                sort_order=product.features.count(),
            )
            _toast(request, "Feature added.")

        elif action == "delete_feature":
            ProductFeature.objects.filter(pk=request.POST.get("feat_pk"), product=product).delete()
            _toast(request, "Feature removed.")

        elif action == "add_pricing":
            price_raw = request.POST.get("price","").strip()
            ProductPricing.objects.create(
                product=product,
                tier_name=request.POST.get("tier_name",""),
                price=price_raw if price_raw else None,
                billing_cycle=request.POST.get("billing_cycle","monthly"),
                features_included=request.POST.get("features_included",""),
                is_featured="is_featured" in request.POST,
                cta_text=request.POST.get("cta_text","Get Started"),
                sort_order=product.pricing_tiers.count(),
            )
            _toast(request, "Pricing tier added.")

        elif action == "delete_pricing":
            ProductPricing.objects.filter(pk=request.POST.get("pricing_pk"), product=product).delete()
            _toast(request, "Pricing tier removed.")

        elif action == "add_faq":
            ProductFAQ.objects.create(
                product=product,
                question=request.POST.get("question",""),
                answer=request.POST.get("answer",""),
                sort_order=product.faqs.count(),
            )
            _toast(request, "FAQ added.")

        elif action == "delete_faq":
            ProductFAQ.objects.filter(pk=request.POST.get("faq_pk"), product=product).delete()
            _toast(request, "FAQ removed.")

        elif action == "publish":
            product.publish(published_by=request.user)
            _toast(request, f"{product.name} published.")

        elif action == "unpublish":
            product.unpublish()
            _toast(request, f"{product.name} moved to draft.")

        return redirect("admin_panel:product_edit", pk=pk)

    return render(request, "admin_panel/products/edit.html", {
        "product": product,
        "features": product.features.order_by("sort_order"),
        "pricing":  product.pricing_tiers.order_by("sort_order"),
        "faqs":     product.faqs.order_by("sort_order"),
        "billing_choices": ProductPricing.BillingCycle.choices,
        "stats": get_dashboard_stats(),
        "page_title": f"Product — {product.name}", "active_nav": "products",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# NEWSLETTER
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def newsletter_subscribers(request):
    from apps.newsletter.models import NewsletterSubscriber
    qs = NewsletterSubscriber.objects.order_by("-created_at")
    if request.GET.get("status"): qs = qs.filter(status=request.GET["status"])
    page = Paginator(qs, 30).get_page(request.GET.get("page",1))
    return render(request, "admin_panel/newsletter/subscribers.html", {
        "subscribers": page,
        "status_choices": NewsletterSubscriber.Status.choices,
        "status_filter": request.GET.get("status",""),
        "stats": get_dashboard_stats(),
        "page_title": "Subscribers", "active_nav": "newsletter",
    })


@admin_required
def newsletter_campaigns(request):
    from apps.newsletter.models import NewsletterCampaign
    campaigns = NewsletterCampaign.objects.order_by("-created_at")
    return render(request, "admin_panel/newsletter/campaigns.html", {
        "campaigns": campaigns,
        "stats": get_dashboard_stats(),
        "page_title": "Campaigns", "active_nav": "newsletter",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def newsletter_campaign_create(request):
    from apps.newsletter.models import NewsletterCampaign
    if request.method == "POST":
        campaign = NewsletterCampaign.objects.create(
            subject=request.POST.get("subject",""),
            preview_text=request.POST.get("preview_text",""),
            content_html=request.POST.get("content_html",""),
            content_text=request.POST.get("content_text",""),
            created_by=request.user,
        )
        _toast(request, "Campaign created.")
        return redirect("admin_panel:newsletter_campaign_edit", pk=campaign.pk)
    return render(request, "admin_panel/newsletter/campaign_form.html", {
        "action": "Create", "campaign": None,
        "stats": get_dashboard_stats(),
        "page_title": "New Campaign", "active_nav": "newsletter",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def newsletter_campaign_edit(request, pk):
    from apps.newsletter.models import NewsletterCampaign
    from apps.newsletter.services import send_campaign
    campaign = get_object_or_404(NewsletterCampaign, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action","save")
        if action == "save":
            campaign.subject      = request.POST.get("subject", campaign.subject)
            campaign.preview_text = request.POST.get("preview_text", campaign.preview_text)
            campaign.content_html = request.POST.get("content_html", campaign.content_html)
            campaign.content_text = request.POST.get("content_text", campaign.content_text)
            campaign.save()
            _toast(request, "Campaign saved.")
        elif action == "send":
            try:
                count = send_campaign(campaign)
                _toast(request, f"Campaign queued for {count} subscribers.")
            except ValueError as e:
                _toast(request, str(e), "error")
        return redirect("admin_panel:newsletter_campaign_edit", pk=pk)
    return render(request, "admin_panel/newsletter/campaign_form.html", {
        "action": "Edit", "campaign": campaign,
        "stats": get_dashboard_stats(),
        "page_title": f"Campaign — {campaign.subject}", "active_nav": "newsletter",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# MEDIA LIBRARY
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def media_library(request):
    from apps.media.models import MediaFile, MediaFolder
    from apps.media.selectors import get_all_files
    folder_id = request.GET.get("folder")
    file_type = request.GET.get("type","")
    folder    = MediaFolder.objects.filter(pk=folder_id).first() if folder_id else None
    files     = get_all_files(file_type=file_type or None, folder=folder)
    folders   = MediaFolder.objects.filter(parent=folder).order_by("name")
    return render(request, "admin_panel/media/library.html", {
        "files": files, "folders": folders,
        "current_folder": folder,
        "file_type": file_type,
        "stats": get_dashboard_stats(),
        "page_title": "Media Library", "active_nav": "media",
    })


@admin_required
@require_POST
def media_upload(request):
    from apps.media.services import upload_file
    from apps.media.models import MediaFolder
    folder_id = request.POST.get("folder_id")
    folder    = MediaFolder.objects.filter(pk=folder_id).first() if folder_id else None
    uploaded  = []
    errors    = []
    for f in request.FILES.getlist("files"):
        try:
            mf = upload_file(f, folder=folder, uploaded_by=request.user)
            uploaded.append({"id": str(mf.pk), "name": mf.title, "url": mf.file.url})
        except ValueError as e:
            errors.append(str(e))
    return JsonResponse({"uploaded": uploaded, "errors": errors})


@admin_required
@require_POST
def media_delete(request, pk):
    from apps.media.models import MediaFile
    mf = get_object_or_404(MediaFile, pk=pk)
    try:
        if mf.file and os.path.exists(mf.file.path):
            os.remove(mf.file.path)
    except Exception:
        pass
    mf.delete()
    if _htmx(request):
        return JsonResponse({"ok": True})
    _toast(request, "File deleted.")
    return redirect("admin_panel:media_library")


# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def site_settings(request):
    from apps.integrations.models import SiteSettings
    settings_obj = SiteSettings.load()
    if request.method == "POST":
        for field in ["ga4_measurement_id","gtm_container_id","meta_pixel_id",
                      "clarity_project_id","whatsapp_phone","whatsapp_message",
                      "whatsapp_tooltip","chatbot_name","chatbot_greeting",
                      "chatbot_system_prompt","captcha_site_key","captcha_provider"]:
            if field in request.POST:
                setattr(settings_obj, field, request.POST[field])
        for field in ["whatsapp_enabled","chatbot_enabled","captcha_enabled"]:
            setattr(settings_obj, field, field in request.POST)
        settings_obj.save()
        if _htmx(request):
            return render(request, "admin_panel/components/toast_trigger.html",
                          {"message": "Settings saved!", "type": "success"})
        _toast(request, "Settings saved.")
        return redirect("admin_panel:settings")
    return render(request, "admin_panel/settings/index.html", {
        "settings": settings_obj,
        "stats": get_dashboard_stats(),
        "page_title": "Site Settings", "active_nav": "settings",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL FAQS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def faqs_list(request):
    from apps.settings_app.models import GlobalFAQ
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            GlobalFAQ.objects.create(
                question=request.POST.get("question","").strip(),
                answer=request.POST.get("answer","").strip(),
                category=request.POST.get("category","general"),
                sort_order=GlobalFAQ.objects.count(),
            )
            _toast(request, "FAQ added.")
        elif action == "delete":
            GlobalFAQ.objects.filter(pk=request.POST.get("pk")).delete()
            _toast(request, "FAQ deleted.")
        elif action == "toggle":
            faq = GlobalFAQ.objects.filter(pk=request.POST.get("pk")).first()
            if faq:
                faq.is_active = not faq.is_active
                faq.save(update_fields=["is_active"])
        return redirect("admin_panel:faqs_list")

    faqs = GlobalFAQ.objects.order_by("category","sort_order")
    return render(request, "admin_panel/faqs/list.html", {
        "faqs": faqs,
        "categories": GlobalFAQ.FAQCategory.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Global FAQs", "active_nav": "faqs",
    })


@admin_required
@require_http_methods(["GET","POST"])
def faq_edit(request, pk):
    from apps.settings_app.models import GlobalFAQ
    faq = get_object_or_404(GlobalFAQ, pk=pk)
    if request.method == "POST":
        faq.question   = request.POST.get("question", faq.question)
        faq.answer     = request.POST.get("answer", faq.answer)
        faq.category   = request.POST.get("category", faq.category)
        faq.sort_order = int(request.POST.get("sort_order", faq.sort_order))
        faq.save()
        _toast(request, "FAQ updated.")
        return redirect("admin_panel:faqs_list")
    from apps.settings_app.models import GlobalFAQ as GFAQ
    return render(request, "admin_panel/faqs/edit.html", {
        "faq": faq, "categories": GFAQ.FAQCategory.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Edit FAQ", "active_nav": "faqs",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# TESTIMONIALS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def testimonials_list(request):
    from apps.settings_app.models import Testimonial
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            Testimonial.objects.filter(pk=request.POST.get("pk")).update(status="approved")
            _toast(request, "Testimonial approved.")
        elif action == "reject":
            Testimonial.objects.filter(pk=request.POST.get("pk")).update(status="rejected")
            _toast(request, "Testimonial rejected.")
        elif action == "delete":
            Testimonial.objects.filter(pk=request.POST.get("pk")).delete()
            _toast(request, "Testimonial deleted.")
        elif action == "toggle_featured":
            t = Testimonial.objects.filter(pk=request.POST.get("pk")).first()
            if t:
                t.is_featured = not t.is_featured
                t.save(update_fields=["is_featured"])
        return redirect("admin_panel:testimonials_list")

    testimonials = Testimonial.objects.order_by("sort_order","-created_at")
    return render(request, "admin_panel/testimonials/list.html", {
        "testimonials": testimonials,
        "stats": get_dashboard_stats(),
        "page_title": "Testimonials", "active_nav": "testimonials",
    })


@admin_required
@require_http_methods(["GET","POST"])
def testimonial_create(request):
    from apps.settings_app.models import Testimonial
    if request.method == "POST":
        t = Testimonial(
            customer_name=request.POST.get("customer_name","").strip(),
            designation=request.POST.get("designation","").strip(),
            clinic_name=request.POST.get("clinic_name","").strip(),
            location=request.POST.get("location","").strip(),
            rating=int(request.POST.get("rating",5)),
            feedback=request.POST.get("feedback","").strip(),
            product=request.POST.get("product","").strip(),
            status=request.POST.get("status","approved"),
            is_featured="is_featured" in request.POST,
            sort_order=Testimonial.objects.count(),
        )
        if "photo" in request.FILES:
            t.photo = request.FILES["photo"]
        t.save()
        _toast(request, "Testimonial added.")
        return redirect("admin_panel:testimonials_list")
    return render(request, "admin_panel/testimonials/form.html", {
        "action": "Add", "testimonial": None,
        "stats": get_dashboard_stats(),
        "page_title": "Add Testimonial", "active_nav": "testimonials",
    })


@admin_required
@require_http_methods(["GET","POST"])
def testimonial_edit(request, pk):
    from apps.settings_app.models import Testimonial
    t = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        t.customer_name = request.POST.get("customer_name", t.customer_name)
        t.designation   = request.POST.get("designation", t.designation)
        t.clinic_name   = request.POST.get("clinic_name", t.clinic_name)
        t.location      = request.POST.get("location", t.location)
        t.rating        = int(request.POST.get("rating", t.rating))
        t.feedback      = request.POST.get("feedback", t.feedback)
        t.product       = request.POST.get("product", t.product)
        t.status        = request.POST.get("status", t.status)
        t.is_featured   = "is_featured" in request.POST
        t.sort_order    = int(request.POST.get("sort_order", t.sort_order))
        if "photo" in request.FILES:
            t.photo = request.FILES["photo"]
        t.save()
        _toast(request, "Testimonial updated.")
        return redirect("admin_panel:testimonials_list")
    from apps.settings_app.models import Testimonial as TM
    return render(request, "admin_panel/testimonials/form.html", {
        "action": "Edit", "testimonial": t,
        "status_choices": TM.Status.choices,
        "stats": get_dashboard_stats(),
        "page_title": f"Edit — {t.customer_name}", "active_nav": "testimonials",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def users_list(request):
    from apps.accounts.models import User
    users = User.objects.order_by("email")
    return render(request, "admin_panel/users/list.html", {
        "users": users,
        "stats": get_dashboard_stats(),
        "page_title": "Users", "active_nav": "users",
    })


@admin_required
@require_http_methods(["GET","POST"])
def user_create(request):
    from apps.accounts.models import User
    from django.contrib.auth.hashers import make_password
    error = None
    if request.method == "POST":
        email = request.POST.get("email","").strip().lower()
        fname = request.POST.get("first_name","").strip()
        lname = request.POST.get("last_name","").strip()
        password = request.POST.get("password","")
        is_staff = "is_staff" in request.POST
        is_superuser = "is_superuser" in request.POST

        if not email or not password:
            error = "Email and password are required."
        elif User.objects.filter(email=email).exists():
            error = f"A user with email {email} already exists."
        else:
            user = User.objects.create_user(
                email=email, password=password,
                first_name=fname, last_name=lname,
                is_staff=is_staff, is_superuser=is_superuser,
            )
            _toast(request, f"User {email} created.")
            return redirect("admin_panel:users_list")

    return render(request, "admin_panel/users/form.html", {
        "action": "Create", "user_obj": None, "error": error,
        "stats": get_dashboard_stats(),
        "page_title": "Create User", "active_nav": "users",
    })


@admin_required
@require_http_methods(["GET","POST"])
def user_edit(request, pk):
    from apps.accounts.models import User
    user_obj = get_object_or_404(User, pk=pk)
    error = None
    if request.method == "POST":
        action = request.POST.get("action","save")
        if action == "suspend":
            user_obj.is_active = False
            user_obj.save(update_fields=["is_active"])
            _toast(request, f"User {user_obj.email} suspended.")
            return redirect("admin_panel:users_list")
        elif action == "activate":
            user_obj.is_active = True
            user_obj.save(update_fields=["is_active"])
            _toast(request, f"User {user_obj.email} activated.")
            return redirect("admin_panel:users_list")
        else:
            user_obj.first_name  = request.POST.get("first_name", user_obj.first_name)
            user_obj.last_name   = request.POST.get("last_name", user_obj.last_name)
            user_obj.is_staff    = "is_staff" in request.POST
            user_obj.is_superuser= "is_superuser" in request.POST
            new_password = request.POST.get("new_password","").strip()
            if new_password:
                user_obj.set_password(new_password)
            user_obj.save()
            _toast(request, "User updated.")
            return redirect("admin_panel:users_list")

    return render(request, "admin_panel/users/form.html", {
        "action": "Edit", "user_obj": user_obj, "error": error,
        "stats": get_dashboard_stats(),
        "page_title": f"Edit — {user_obj.email}", "active_nav": "users",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOGS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def audit_logs(request):
    # Use Django's built-in LogEntry for audit trail
    from django.contrib.admin.models import LogEntry
    logs = LogEntry.objects.select_related("user","content_type").order_by("-action_time")
    page = Paginator(logs, 30).get_page(request.GET.get("page",1))
    return render(request, "admin_panel/audit/logs.html", {
        "logs": page,
        "stats": get_dashboard_stats(),
        "page_title": "Audit Logs", "active_nav": "audit",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED SETTINGS (SMTP, SOCIAL, ANNOUNCEMENT, ROBOTS, REDIRECTS)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def advanced_settings(request):
    from apps.settings_app.models import SMTPSettings, SocialLinks, AnnouncementBar, RobotsTxt
    from apps.seo.models import Redirect

    smtp      = SMTPSettings.load()
    social    = SocialLinks.load()
    robots    = RobotsTxt.load()
    announcements = AnnouncementBar.objects.order_by("-created_at")
    redirects     = Redirect.objects.order_by("old_path")[:50]

    if request.method == "POST":
        section = request.POST.get("section")

        if section == "smtp":
            smtp.host       = request.POST.get("host", smtp.host)
            smtp.port       = int(request.POST.get("port", smtp.port))
            smtp.username   = request.POST.get("username", smtp.username)
            smtp.from_email = request.POST.get("from_email", smtp.from_email)
            smtp.from_name  = request.POST.get("from_name", smtp.from_name)
            smtp.use_tls    = "use_tls" in request.POST
            smtp.use_ssl    = "use_ssl" in request.POST
            smtp.save()
            # Apply to Django settings at runtime
            from django.conf import settings as dj_settings
            dj_settings.EMAIL_HOST         = smtp.host
            dj_settings.EMAIL_PORT         = smtp.port
            dj_settings.EMAIL_HOST_USER    = smtp.username
            dj_settings.EMAIL_USE_TLS      = smtp.use_tls
            dj_settings.EMAIL_USE_SSL      = smtp.use_ssl
            dj_settings.DEFAULT_FROM_EMAIL = smtp.display_from
            _toast(request, "SMTP settings saved.")

        elif section == "smtp_test":
            from django.core.mail import send_mail
            test_email = request.POST.get("test_email","").strip()
            if test_email:
                try:
                    send_mail(
                        subject="CuraSuite SMTP Test",
                        message="Your SMTP configuration is working correctly.",
                        from_email=smtp.display_from,
                        recipient_list=[test_email],
                    )
                    smtp.is_verified = True
                    smtp.save(update_fields=["is_verified"])
                    _toast(request, f"Test email sent to {test_email}!")
                except Exception as e:
                    _toast(request, f"SMTP Error: {e}", "error")

        elif section == "social":
            for field in ["facebook","instagram","linkedin","twitter_x","youtube","whatsapp_link"]:
                setattr(social, field, request.POST.get(field, getattr(social, field)))
            social.save()
            _toast(request, "Social links saved.")

        elif section == "announcement_create":
            AnnouncementBar.objects.create(
                text=request.POST.get("text",""),
                link_text=request.POST.get("link_text",""),
                link_url=request.POST.get("link_url",""),
                style=request.POST.get("style","info"),
                is_active="is_active" in request.POST,
                is_dismissible="is_dismissible" in request.POST,
            )
            _toast(request, "Announcement created.")

        elif section == "announcement_toggle":
            ann = AnnouncementBar.objects.filter(pk=request.POST.get("pk")).first()
            if ann:
                ann.is_active = not ann.is_active
                ann.save(update_fields=["is_active"])
                _toast(request, "Announcement updated.")

        elif section == "announcement_delete":
            AnnouncementBar.objects.filter(pk=request.POST.get("pk")).delete()
            _toast(request, "Announcement deleted.")

        elif section == "robots":
            robots.content = request.POST.get("content", robots.content)
            robots.save()
            _toast(request, "robots.txt saved.")

        elif section == "redirect_create":
            old_path = request.POST.get("old_path","").strip()
            new_path = request.POST.get("new_path","").strip()
            if old_path and new_path:
                Redirect.objects.update_or_create(
                    old_path=old_path,
                    defaults={
                        "new_path": new_path,
                        "redirect_type": request.POST.get("redirect_type","301"),
                        "is_active": True,
                        "note": request.POST.get("note",""),
                    }
                )
                _toast(request, f"Redirect {old_path} → {new_path} saved.")

        elif section == "redirect_delete":
            Redirect.objects.filter(pk=request.POST.get("pk")).delete()
            _toast(request, "Redirect deleted.")

        return redirect("admin_panel:advanced_settings")

    return render(request, "admin_panel/settings/advanced.html", {
        "smtp": smtp, "social": social, "robots": robots,
        "announcements": announcements, "redirects": redirects,
        "bar_styles": AnnouncementBar.BarStyle.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Advanced Settings", "active_nav": "advanced_settings",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# BLOG COMMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def blog_comments(request):
    from apps.blogs.models import BlogComment
    if request.method == "POST":
        pk     = request.POST.get("pk")
        action = request.POST.get("action")
        comment = BlogComment.objects.filter(pk=pk).first()
        if comment:
            if action == "approve":
                comment.status = BlogComment.Status.APPROVED
                comment.save(update_fields=["status"])
                _toast(request, "Comment approved.")
            elif action == "spam":
                comment.status = BlogComment.Status.SPAM
                comment.save(update_fields=["status"])
                _toast(request, "Marked as spam.")
            elif action == "delete":
                comment.delete()
                _toast(request, "Comment deleted.")
        return redirect("admin_panel:blog_comments")

    status_filter = request.GET.get("status","pending")
    comments = BlogComment.objects.filter(status=status_filter).select_related("blog").order_by("-created_at")
    page = Paginator(comments, 20).get_page(request.GET.get("page",1))
    return render(request, "admin_panel/blogs/comments.html", {
        "comments": page, "status_filter": status_filter,
        "stats": get_dashboard_stats(),
        "page_title": "Blog Comments", "active_nav": "blogs",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT CREATE (new product from scratch)
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
@require_http_methods(["GET","POST"])
def product_create(request):
    from apps.products.models import Product
    error = None
    if request.method == "POST":
        key = request.POST.get("key","").strip().lower().replace(" ","-")
        name = request.POST.get("name","").strip()
        if not key or not name:
            error = "Key and name are required."
        elif Product.all_objects.filter(key=key).exists():
            error = f"A product with key '{key}' already exists."
        else:
            from apps.products.services import create_product
            product = create_product(
                key=key, name=name,
                tagline=request.POST.get("tagline",""),
                short_description=request.POST.get("short_description",""),
                long_description=request.POST.get("long_description",""),
                target_audience=request.POST.get("target_audience",""),
                color=request.POST.get("color","#2563EB"),
                sort_order=Product.all_objects.count(),
                created_by=request.user,
            )
            _toast(request, f'Product "{name}" created.')
            return redirect("admin_panel:product_edit", pk=product.pk)

    return render(request, "admin_panel/products/create.html", {
        "error": error,
        "stats": get_dashboard_stats(),
        "page_title": "New Product", "active_nav": "products",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# MANUAL LEAD CREATE
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
@require_http_methods(["GET","POST"])
def crm_lead_create(request):
    from apps.crm.models import Lead
    from apps.crm.services import capture_lead
    error = None
    if request.method == "POST":
        full_name = request.POST.get("full_name","").strip()
        email     = request.POST.get("email","").strip().lower()
        if not full_name or not email:
            error = "Name and email are required."
        else:
            lead, created = capture_lead(
                full_name=full_name,
                email=email,
                phone=request.POST.get("phone",""),
                organization=request.POST.get("organization",""),
                city=request.POST.get("city",""),
                message=request.POST.get("message",""),
                business_type=request.POST.get("business_type",""),
                product_interest=request.POST.get("product_interest",""),
                source=request.POST.get("source", Lead.Source.DIRECT),
            )
            if not created:
                _toast(request, f"Lead already exists — opened existing record.")
            else:
                _toast(request, f"Lead '{full_name}' created.")
            return redirect("admin_panel:crm_lead_detail", pk=lead.pk)

    from apps.crm.models import Lead as LeadModel
    return render(request, "admin_panel/crm/create.html", {
        "error": error,
        "source_choices": LeadModel.Source.choices,
        "business_type_choices": LeadModel.BusinessType.choices,
        "stats": get_dashboard_stats(),
        "page_title": "Add Lead", "active_nav": "crm",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PRICING MANAGER  — /manage/pricing/
# Central view to manage all product pricing tiers across all products
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def pricing_list(request):
    """Overview of all pricing tiers across all products."""
    from apps.products.models import Product, ProductPricing
    products = Product.all_objects.filter(
        deleted_at__isnull=True
    ).prefetch_related("pricing_tiers").order_by("sort_order")
    return render(request, "admin_panel/pricing/list.html", {
        "products": products,
        "stats": get_dashboard_stats(),
        "page_title": "Pricing Manager",
        "active_nav": "pricing",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def pricing_create(request, product_pk):
    """Add a new pricing tier to a specific product."""
    from apps.products.models import Product, ProductPricing
    product = get_object_or_404(Product.all_objects, pk=product_pk)

    if request.method == "POST":
        price_raw = request.POST.get("price", "").strip()
        original_price_raw = request.POST.get("original_price", "").strip()
        ProductPricing.objects.create(
            product=product,
            tier_name=request.POST.get("tier_name", "").strip(),
            price=price_raw if price_raw else None,
            original_price=original_price_raw if original_price_raw else None,
            billing_cycle=request.POST.get("billing_cycle", "yearly"),
            description=request.POST.get("description", "").strip(),
            features_included=request.POST.get("features_included", "").strip(),
            is_featured="is_featured" in request.POST,
            cta_text=request.POST.get("cta_text", "Get Started").strip(),
            cta_url=request.POST.get("cta_url", "").strip(),
            sort_order=product.pricing_tiers.count(),
        )
        _toast(request, f"Pricing tier added to {product.name}.")
        return redirect("admin_panel:pricing_list")

    from apps.products.models import ProductPricing as PP
    return render(request, "admin_panel/pricing/form.html", {
        "action": "Add",
        "product": product,
        "tier": None,
        "billing_choices": PP.BillingCycle.choices,
        "stats": get_dashboard_stats(),
        "page_title": f"Add Tier — {product.name}",
        "active_nav": "pricing",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def pricing_edit(request, pk):
    """Edit an existing pricing tier."""
    from apps.products.models import ProductPricing
    tier = get_object_or_404(ProductPricing, pk=pk)
    product = tier.product

    if request.method == "POST":
        action = request.POST.get("action", "save")
        if action == "delete":
            name = tier.tier_name
            tier.delete()
            _toast(request, f'Tier "{name}" deleted.')
            return redirect("admin_panel:pricing_list")

        price_raw = request.POST.get("price", "").strip()
        original_price_raw = request.POST.get("original_price", "").strip()
        tier.tier_name        = request.POST.get("tier_name", tier.tier_name).strip()
        tier.price            = price_raw if price_raw else None
        tier.original_price   = original_price_raw if original_price_raw else None
        tier.billing_cycle    = request.POST.get("billing_cycle", tier.billing_cycle)
        tier.description      = request.POST.get("description", tier.description).strip()
        tier.features_included= request.POST.get("features_included", tier.features_included).strip()
        tier.is_featured      = "is_featured" in request.POST
        tier.cta_text         = request.POST.get("cta_text", tier.cta_text).strip()
        tier.cta_url          = request.POST.get("cta_url", tier.cta_url).strip()
        tier.sort_order       = int(request.POST.get("sort_order", tier.sort_order))
        tier.save()
        _toast(request, f'Tier "{tier.tier_name}" saved.')
        return redirect("admin_panel:pricing_list")

    return render(request, "admin_panel/pricing/form.html", {
        "action": "Edit",
        "product": product,
        "tier": tier,
        "billing_choices": tier.BillingCycle.choices,
        "stats": get_dashboard_stats(),
        "page_title": f"Edit — {tier.tier_name}",
        "active_nav": "pricing",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# LANDING PAGES  — /manage/landing-pages/
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def landing_pages_list(request):
    from apps.landing_pages.models import LandingPage
    pages = LandingPage.all_objects.select_related("product").order_by("product__sort_order", "slug")
    return render(request, "admin_panel/landing_pages/list.html", {
        "pages": pages,
        "stats": get_dashboard_stats(),
        "page_title": "Landing Pages", "active_nav": "landing_pages",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def landing_page_create(request):
    from apps.landing_pages.models import LandingPage
    from apps.products.models import Product
    error = None
    if request.method == "POST":
        slug = request.POST.get("slug", "").strip().lower().replace(" ", "-")
        headline = request.POST.get("headline", "").strip()
        product_id = request.POST.get("product")
        if not slug or not headline or not product_id:
            error = "Slug, headline, and product are required."
        elif LandingPage.all_objects.filter(slug=slug).exists():
            error = f"A landing page with slug '{slug}' already exists."
        else:
            lp = LandingPage.objects.create(
                slug=slug, headline=headline,
                product_id=product_id,
                subheadline=request.POST.get("subheadline", ""),
                target_audience_label=request.POST.get("target_audience_label", ""),
                specialty=request.POST.get("specialty", ""),
                social_proof_note=request.POST.get("social_proof_note", ""),
                whatsapp_message_template=request.POST.get("whatsapp_message_template", ""),
                default_utm_campaign=request.POST.get("default_utm_campaign", ""),
                noindex="noindex" in request.POST,
            )
            _toast(request, f'Landing page "{headline}" created.')
            return redirect("admin_panel:landing_page_edit", pk=lp.pk)

    return render(request, "admin_panel/landing_pages/form.html", {
        "action": "Create", "lp": None, "error": error,
        "products": Product.objects.order_by("sort_order"),
        "specialty_choices": _lead_specialty_choices(),
        "stats": get_dashboard_stats(),
        "page_title": "New Landing Page", "active_nav": "landing_pages",
    })


def _lead_specialty_choices():
    from apps.crm.models import Lead
    return Lead.Specialty.choices


@admin_required
@require_http_methods(["GET", "POST"])
def landing_page_edit(request, pk):
    from apps.landing_pages.models import LandingPage, LandingPainPoint, LandingBenefit
    from apps.products.models import Product
    lp = get_object_or_404(LandingPage.all_objects, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        if action == "save_details":
            lp.headline               = request.POST.get("headline", lp.headline)
            lp.subheadline            = request.POST.get("subheadline", lp.subheadline)
            lp.target_audience_label  = request.POST.get("target_audience_label", lp.target_audience_label)
            lp.specialty              = request.POST.get("specialty", lp.specialty)
            lp.social_proof_note      = request.POST.get("social_proof_note", lp.social_proof_note)
            lp.whatsapp_message_template = request.POST.get("whatsapp_message_template", lp.whatsapp_message_template)
            lp.default_utm_campaign   = request.POST.get("default_utm_campaign", lp.default_utm_campaign)
            lp.noindex                = "noindex" in request.POST
            if "hero_image" in request.FILES:
                lp.hero_image = request.FILES["hero_image"]
            lp.save()
            _toast(request, "Landing page details saved.")

        elif action == "add_pain_point":
            text = request.POST.get("pain_text", "").strip()
            consequence_text = request.POST.get("pain_consequence", "").strip()
            solution_text = request.POST.get("pain_solution", "").strip()
            if text:
                LandingPainPoint.objects.create(
                    landing_page=lp, text=text, consequence_text=consequence_text,
                    solution_text=solution_text, sort_order=lp.pain_points.count(),
                )
                _toast(request, "Pain point added.")

        elif action == "delete_pain_point":
            LandingPainPoint.objects.filter(pk=request.POST.get("pain_pk"), landing_page=lp).delete()
            _toast(request, "Pain point removed.")

        elif action == "add_benefit":
            LandingBenefit.objects.create(
                landing_page=lp,
                icon=request.POST.get("benefit_icon", "✓"),
                title=request.POST.get("benefit_title", ""),
                description=request.POST.get("benefit_description", ""),
                sort_order=lp.benefits.count(),
            )
            _toast(request, "Benefit added.")

        elif action == "delete_benefit":
            LandingBenefit.objects.filter(pk=request.POST.get("benefit_pk"), landing_page=lp).delete()
            _toast(request, "Benefit removed.")

        elif action == "publish":
            lp.publish(published_by=request.user)
            _toast(request, f'"{lp.headline}" published — live at /lp/{lp.slug}/')

        elif action == "unpublish":
            lp.unpublish()
            _toast(request, "Landing page unpublished.")

        elif action == "delete":
            headline = lp.headline
            lp.soft_delete()
            _toast(request, f'"{headline}" deleted.')
            return redirect("admin_panel:landing_pages_list")

        return redirect("admin_panel:landing_page_edit", pk=pk)

    return render(request, "admin_panel/landing_pages/form.html", {
        "action": "Edit", "lp": lp, "error": None,
        "products": Product.objects.order_by("sort_order"),
        "specialty_choices": _lead_specialty_choices(),
        "pain_points": lp.pain_points.all(),
        "benefits": lp.benefits.all(),
        "stats": get_dashboard_stats(),
        "page_title": f"Landing Page — {lp.headline}", "active_nav": "landing_pages",
    })
