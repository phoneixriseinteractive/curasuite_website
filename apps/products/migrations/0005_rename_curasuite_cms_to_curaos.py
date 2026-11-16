"""
Rename the clinic-management product "CuraSuite CMS" to "CuraOS" in stored data.

"CuraSuite" on its own is also the company/ecosystem brand, so it is only replaced
inside records that belong to the product itself (its fields, features, FAQs, pricing
tiers and SEO metadata). Elsewhere only the explicit product name "CuraSuite CMS" is
replaced. The product's internal `key` stays "curasuite".

Reversing restores the product name/slug, redirect target and the CRM/testimonial
product values; free-text replacements are left as they are.
"""

from django.db import migrations

PRODUCT_KEY = "curasuite"
OLD_SLUG, NEW_SLUG = "curasuite", "curaos"
OLD_NAME, NEW_NAME = "CuraSuite CMS", "CuraOS"


def _replace(queryset, fields, old, new):
    for obj in queryset:
        changed = []
        for field in fields:
            value = getattr(obj, field) or ""
            if old in value:
                setattr(obj, field, value.replace(old, new))
                changed.append(field)
        if changed:
            obj.save(update_fields=changed)


def _product_text(value):
    return value.replace(OLD_NAME, NEW_NAME).replace("CuraSuite", NEW_NAME)


def forwards(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductFeature = apps.get_model("products", "ProductFeature")
    ProductFAQ = apps.get_model("products", "ProductFAQ")
    ProductPricing = apps.get_model("products", "ProductPricing")
    ContentType = apps.get_model("contenttypes", "ContentType")
    SEOMetadata = apps.get_model("seo", "SEOMetadata")
    Redirect = apps.get_model("seo", "Redirect")
    Lead = apps.get_model("crm", "Lead")
    DemoRequest = apps.get_model("crm", "DemoRequest")
    Testimonial = apps.get_model("settings_app", "Testimonial")
    GlobalFAQ = apps.get_model("settings_app", "GlobalFAQ")
    Blog = apps.get_model("blogs", "Blog")
    SiteSettings = apps.get_model("integrations", "SiteSettings")

    product = Product._base_manager.filter(key=PRODUCT_KEY).first()
    if product:
        product.name = NEW_NAME
        if product.slug == OLD_SLUG:
            product.slug = NEW_SLUG
        for field in ("tagline", "short_description", "long_description"):
            setattr(product, field, _product_text(getattr(product, field) or ""))
        product.save()

        for model, fields in (
            (ProductFeature, ("title", "description")),
            (ProductFAQ, ("question", "answer")),
            (ProductPricing, ("tier_name", "description", "features_included")),
        ):
            for obj in model._base_manager.filter(product=product):
                for field in fields:
                    setattr(obj, field, _product_text(getattr(obj, field) or ""))
                obj.save(update_fields=list(fields))

        ct = ContentType.objects.filter(app_label="products", model="product").first()
        if ct:
            for seo in SEOMetadata._base_manager.filter(content_type=ct, object_id=product.pk):
                for field in ("seo_title", "meta_description", "og_title", "og_description", "focus_keyword"):
                    value = getattr(seo, field, None)
                    if value:
                        # Keep the "| CuraSuite" brand suffix on titles.
                        head, sep, tail = value.rpartition("| CuraSuite")
                        value = _product_text(head) + sep + tail if sep else _product_text(value)
                        setattr(seo, field, value)
                seo.save()

    Redirect._base_manager.filter(new_path=f"/products/{OLD_SLUG}/").update(new_path=f"/products/{NEW_SLUG}/")

    for model in (Lead, DemoRequest):
        model._base_manager.filter(product_interest__in=["CuraSuite", OLD_NAME]).update(product_interest=NEW_NAME)
    Testimonial._base_manager.filter(product__in=["CuraSuite", OLD_NAME]).update(product=NEW_NAME)

    _replace(Testimonial._base_manager.filter(feedback__contains=OLD_NAME), ("feedback",), OLD_NAME, NEW_NAME)
    _replace(GlobalFAQ._base_manager.filter(answer__contains=OLD_NAME), ("question", "answer"), OLD_NAME, NEW_NAME)
    _replace(Blog._base_manager.filter(content__contains=OLD_NAME), ("content", "excerpt"), OLD_NAME, NEW_NAME)
    _replace(SEOMetadata._base_manager.filter(meta_description__contains=OLD_NAME), ("seo_title", "meta_description"), OLD_NAME, NEW_NAME)
    _replace(SiteSettings._base_manager.filter(chatbot_system_prompt__contains=OLD_NAME), ("chatbot_system_prompt",), OLD_NAME, NEW_NAME)


def backwards(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Redirect = apps.get_model("seo", "Redirect")
    Lead = apps.get_model("crm", "Lead")
    DemoRequest = apps.get_model("crm", "DemoRequest")
    Testimonial = apps.get_model("settings_app", "Testimonial")

    Product._base_manager.filter(key=PRODUCT_KEY, slug=NEW_SLUG).update(name=OLD_NAME, slug=OLD_SLUG)
    Redirect._base_manager.filter(new_path=f"/products/{NEW_SLUG}/").update(new_path=f"/products/{OLD_SLUG}/")
    for model in (Lead, DemoRequest):
        model._base_manager.filter(product_interest=NEW_NAME).update(product_interest="CuraSuite")
    Testimonial._base_manager.filter(product=NEW_NAME).update(product="CuraSuite")


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_pricing_quarterly_plus_gst"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("seo", "0001_initial"),
        ("crm", "0002_lead_specialty_alter_lead_email"),
        ("settings_app", "0002_testimonial_specialty"),
        ("blogs", "0001_initial"),
        ("integrations", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
