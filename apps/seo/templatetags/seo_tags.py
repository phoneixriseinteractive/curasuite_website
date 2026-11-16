"""CuraSuite — SEO template tags (JSON-LD structured data)."""

import json

from django import template
from django.utils.safestring import mark_safe

from apps.seo.schema import sitewide_nodes

register = template.Library()

# Escape characters that could close the <script> element or start an HTML
# comment/entity inside it. JSON parsers read the \uXXXX escapes back verbatim.
_SCRIPT_ESCAPES = {ord("<"): "\\u003c", ord(">"): "\\u003e", ord("&"): "\\u0026"}


@register.simple_tag(takes_context=True)
def schema_graph(context):
    """
    Render the page's single JSON-LD ``@graph``: sitewide nodes followed by
    any page-specific ``schema_nodes`` the view put in the context.
    """
    graph = sitewide_nodes() + list(context.get("schema_nodes") or [])
    payload = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False,
        indent=2,
    ).translate(_SCRIPT_ESCAPES)
    return mark_safe(f'<script type="application/ld+json">\n{payload}\n</script>')
