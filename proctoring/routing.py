# chat/routing.py
from django.urls import re_path

from . import consumers
from django.urls import re_path
from .consumers import TeacherExamConsumer, StudentAttemptConsumer

websocket_urlpatterns = [
  
    re_path(r"^ws/exams/(?P<exam_id>\d+)/$", TeacherExamConsumer.as_asgi()),

  
    re_path(r"^ws/attempts/(?P<attempt_id>\d+)/$", StudentAttemptConsumer.as_asgi()),
]
