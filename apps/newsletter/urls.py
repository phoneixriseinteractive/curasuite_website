"""CuraSuite — Newsletter URLs"""
from django.urls import path
from . import views

app_name = "newsletter"

urlpatterns = [
    path("subscribe/",                         views.subscribe_view,    name="subscribe"),
    path("subscribe/success/",                 views.subscribe_success, name="subscribe_success"),
    path("confirm/<uuid:token>/",              views.confirm,           name="confirm"),
    path("unsubscribe/<uuid:token>/",          views.unsubscribe_view,  name="unsubscribe"),
    path("track/open/<uuid:token>/",           views.track_open,        name="track_open"),
]
