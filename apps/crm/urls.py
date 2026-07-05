"""CuraSuite — CRM URLs"""
from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    path("",              views.contact_page,             name="contact"),
    path("success/",      views.contact_success,          name="contact_success"),
    path("demo/",         views.demo_request_htmx,        name="demo_htmx"),
    path("appointment/",  views.appointment_widget_submit, name="appointment_widget"),
]
