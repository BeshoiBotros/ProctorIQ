# subscriptions/urls.py

from django.urls import path
from .views import SubscribeView

urlpatterns = [
    path('subscriptions/', SubscribeView.as_view(), name='subscriptions-list'),
    path('subscriptions/create/', SubscribeView.as_view(), name='subscriptions-create'), 
    path('subscriptions/<int:pk>/', SubscribeView.as_view(), name='subscription-detail'),
]
