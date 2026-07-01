"""
Run this from your project root:
    python fix_pricing_icon.py

Replaces the Pricing sidebar icon in templates/admin_panel/base.html
with the Indian Rupee (₹) icon from Lucide.
"""
import re, sys, os

path = os.path.join("templates", "admin_panel", "base.html")
if not os.path.exists(path):
    print(f"ERROR: {path} not found. Run from project root.")
    sys.exit(1)

content = open(path, encoding="utf-8").read()

if "pricing_list" not in content:
    print("ERROR: Pricing nav item not found in base.html.")
    print("Please apply the pricing_module.zip first.")
    sys.exit(1)

# Replace whatever SVG icon is inside the pricing nav item
new_icon = (
    '<svg class="adm-nav-icon" viewBox="0 0 24 24">\n'
    '          <path d="M6 3h12"/>\n'
    '          <path d="M6 8h12"/>\n'
    '          <path d="m6 13 8.5 8"/>\n'
    '          <path d="M6 13h3"/>\n'
    '          <path d="M9 13c6.667 0 6.667-10 0-10"/>\n'
    '        </svg>'
)

# Find the pricing nav item block and replace its SVG
pattern = re.compile(
    r"({% url 'admin_panel:pricing_list' %}[^>]*>)\s*<svg[^>]*>.*?</svg>",
    re.DOTALL
)
if pattern.search(content):
    content = pattern.sub(r"\1\n        " + new_icon, content)
    open(path, "w", encoding="utf-8").write(content)
    print("✓ Pricing icon updated to Indian Rupee (₹) symbol.")
else:
    print("Could not locate the pricing SVG — trying direct replacement…")
    # Fallback: replace any line-based dollar icon that was injected
    OLD = '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'
    NEW = '<path d="M6 3h12"/><path d="M6 8h12"/><path d="m6 13 8.5 8"/><path d="M6 13h3"/><path d="M9 13c6.667 0 6.667-10 0-10"/>'
    if OLD in content:
        content = content.replace(OLD, NEW)
        open(path, "w", encoding="utf-8").write(content)
        print("✓ Pricing icon updated (fallback method).")
    else:
        print("WARNING: Could not find the old icon. Please update manually:")
        print("In templates/admin_panel/base.html, find the Pricing nav item and")
        print("replace its <svg>...</svg> with:")
        print(new_icon)
