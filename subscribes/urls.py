from django.urls import path
from .views import AdminSubscribeView, TeacherSubscribeView

urlpatterns = [
   
    path('admin/subscriptions/', AdminSubscribeView.as_view(), name='subscriptions-list'), 
    path('admin/subscriptions/<int:pk>/', AdminSubscribeView.as_view(), name='subscription-detail'),  

    path('teacher/subscribe/<int:pk>/', TeacherSubscribeView.as_view(), name='teacher-subscribe'), 
]
