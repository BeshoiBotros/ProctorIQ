# proctoring/urls.py
from django.urls import path
from .views import ProctorNotifyView

urlpatterns = [
    path("notify/", ProctorNotifyView.as_view(), name="proctor-notify"),
]
