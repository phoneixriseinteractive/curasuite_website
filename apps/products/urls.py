"""CuraSuite — Products URLs."""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    # CuraSuite CMS was renamed to CuraOS — keep old links and ads working.
    path("curasuite/", RedirectView.as_view(url="/products/curaos/", permanent=True)),
    path("<slug:slug>/", views.product_detail, name="detail"),
]
