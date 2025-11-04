from django.urls import path
from .views import ExamView

urlpatterns = [
    path('exams/', ExamView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamView.as_view(), name='exam-detail'),
]
