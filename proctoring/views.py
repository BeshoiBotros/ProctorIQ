from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ProctorIQ.utils import IsTeacher
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from exams.models import Exam, ExamAttempt
from .consumers import exam_group, attempt_group

class ProctorNotifyView(APIView):

    permission_classes = [IsTeacher]

    def post(self, request):
        message = request.data.get("message", "")
        exam_id = request.data.get("exam_id")
        attempt_id = request.data.get("attempt_id")

        if not message:
            return Response({"detail": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        channel_layer = get_channel_layer()

   
        if attempt_id:
            attempt = get_object_or_404(ExamAttempt, id=attempt_id)
          
            if attempt.exam.created_by_id != request.user.id:
                return Response({"detail": "Not your exam."}, status=status.HTTP_403_FORBIDDEN)
            async_to_sync(channel_layer.group_send)(
                attempt_group(attempt.id),
                {"type": "exam.message", "payload": {"kind": "direct", "attempt_id": attempt.id, "message": message}}
            )
            return Response({"detail": "Notified the student."})

        if exam_id:
            exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
            async_to_sync(channel_layer.group_send)(
                exam_group(exam.id),
                {"type": "exam.message", "payload": {"kind": "broadcast", "message": message}}
            )
            return Response({"detail": "Broadcast sent."})

        return Response({"detail": "Provide exam_id or attempt_id."}, status=status.HTTP_400_BAD_REQUEST)
