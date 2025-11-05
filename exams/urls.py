from django.urls import path
from .views import *

urlpatterns = [
    # exams
    path('exams/', ExamView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamView.as_view(), name='exam-detail'),

    # questions
    path('exams/<int:exam_id>/questions/', QuestionView.as_view(), name='question-list'),
    path('questions/<int:pk>/', QuestionView.as_view(), name='question-detail'),

    # Choices
    path('questions/<int:question_id>/choices/', ChoiceView.as_view(), name='choice-list'),
    path('choices/<int:pk>/', ChoiceView.as_view(), name='choice-detail'),

    # attempts
    path('attempts/', ExamAttemptView.as_view(), name='attempt-list'),
    path('attempts/<int:pk>/', ExamAttemptView.as_view(), name='attempt-detail'),

    # Student Answer
    path('attempts/<int:attempt_id>/answers/', StudentAnswerView.as_view(), name='answer-list'),
    path('answers/<int:pk>/', StudentAnswerView.as_view(), name='answer-detail'),
]
