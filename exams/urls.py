from django.urls import path
from .views import *

urlpatterns = [
    path('exams/', ExamView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamView.as_view(), name='exam-detail'),


    path('exams/<int:exam_id>/questions/', QuestionView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionView.as_view(), name='question-detail'),
]
