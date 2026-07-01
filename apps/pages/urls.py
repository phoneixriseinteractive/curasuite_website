"""CuraSuite — Pages URLs"""
from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Explicit solutions routes — must come before generic slug catch-all
    # because Django's <slug:slug> doesn't match forward slashes
    path("solutions/doctors/",      views.page_detail, {"slug": "solutions/doctors"},      name="solutions_doctors"),
    path("solutions/clinics/",      views.page_detail, {"slug": "solutions/clinics"},      name="solutions_clinics"),
    path("solutions/pathology-labs/",views.page_detail,{"slug": "solutions/pathology-labs"},name="solutions_labs"),

    # Generic slug catch-all for all other pages (about, pricing, privacy, etc.)
    # <slug:slug> matches [a-zA-Z0-9_-]+ — works for single-segment slugs
    path("<slug:slug>/", views.page_detail, name="detail"),
]
