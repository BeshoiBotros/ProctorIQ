# proctoring/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from exams.models import Exam, ExamAttempt
from django.utils import timezone
from channels.db import database_sync_to_async
from django.utils import timezone
def exam_group(exam_id: int) -> str:
    return f"exam_{exam_id}"

def attempt_group(attempt_id: int) -> str:
    return f"attempt_{attempt_id}"

class TeacherExamConsumer(AsyncJsonWebsocketConsumer):

    @staticmethod
    @database_sync_to_async
    def _get_exam_if_owner(exam_id: int, teacher_id: int):
        from exams.models import Exam
        try:
            return Exam.objects.get(id=exam_id, created_by_id=teacher_id)
        except Exam.DoesNotExist:
            return None

    async def connect(self):
        try:
            self.exam_id = int(self.scope["url_route"]["kwargs"]["exam_id"])
            user = self.scope.get("user")
            if not user or not user.is_authenticated or getattr(user, "role", None) != "Teacher":
                await self.close(code=4001); return
            exam = await self._get_exam_if_owner(self.exam_id, user.id)
            if not exam:
                await self.close(code=4003); return

            self.exam_group_name = f"exam_{self.exam_id}"
            await self.channel_layer.group_add(self.exam_group_name, self.channel_name)
            await self.accept()
        except Exception as e:
         
            print("[TeacherExamConsumer.connect] ERROR:", e)
            await self.close(code=1011) 
            return

    async def disconnect(self, code):
        if hasattr(self, "exam_group_name"):
            await self.channel_layer.group_discard(self.exam_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")

        if action == "broadcast":
            message = content.get("message", "")
            await self.channel_layer.group_send(
                self.exam_group_name,
                {"type": "exam.message", "payload": {"kind": "broadcast", "message": message}}
            )
        elif action == "notify_student":
            target_attempt_id = content.get("attempt_id")
            message = content.get("message", "")
            if not target_attempt_id:
                await self.send_json({"error": "attempt_id required"})
                return
            await self.channel_layer.group_send(
                attempt_group(int(target_attempt_id)),
                {"type": "exam.message", "payload": {"kind": "direct", "attempt_id": target_attempt_id, "message": message}}
            )
        else:
            await self.send_json({"error": "Unknown action"})

    async def exam_message(self, event):
        await self.send_json(event["payload"])

    @staticmethod
    async def _aget_exam_if_owner(exam_id: int, teacher_id: int):
       
        try:
            return await Exam.objects.aget(id=exam_id, created_by_id=teacher_id)
        except Exam.DoesNotExist:
            return None


class StudentAttemptConsumer(AsyncJsonWebsocketConsumer):

    @staticmethod
    @database_sync_to_async
    def _get_attempt_if_owner(attempt_id: int, student_id: int):
        from exams.models import ExamAttempt
        try:
            return ExamAttempt.objects.select_related("exam").get(id=attempt_id, student_id=student_id)
        except ExamAttempt.DoesNotExist:
            return None

    async def connect(self):
        try:
            self.attempt_id = int(self.scope["url_route"]["kwargs"]["attempt_id"])
            user = self.scope.get("user")
            if not user or not user.is_authenticated or getattr(user, "role", None) != "Student":
                await self.close(code=4001); return

            attempt = await self._get_attempt_if_owner(self.attempt_id, user.id)
            if not attempt:
                await self.close(code=4003); return

           
            now = timezone.now()
            if not (attempt.exam.start_time <= now <= attempt.exam.end_time) or not attempt.exam.is_active:
                await self.close(code=4004); return

            self.exam_group_name = f"exam_{attempt.exam_id}"
            self.attempt_group_name = f"attempt_{self.attempt_id}"
            await self.channel_layer.group_add(self.exam_group_name, self.channel_name)
            await self.channel_layer.group_add(self.attempt_group_name, self.channel_name)
            await self.accept()

        
            await self.channel_layer.group_send(
                self.exam_group_name,
                {"type": "exam.message", "payload": {"kind": "student_joined", "attempt_id": self.attempt_id}}
            )
        except Exception as e:
            print("[StudentAttemptConsumer.connect] ERROR:", e)
            await self.close(code=1011)
            return
    async def disconnect(self, code):
        if hasattr(self, "exam_group_name"):
            await self.channel_layer.group_discard(self.exam_group_name, self.channel_name)
        if hasattr(self, "attempt_group_name"):
            await self.channel_layer.group_discard(self.attempt_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action == "ping":
          
            await self.channel_layer.group_send(
                self.exam_group_name,
                {"type": "exam.message", "payload": {"kind": "ping", "attempt_id": self.attempt_id}}
            )
        else:
            await self.send_json({"error": "Unknown action"})

    async def exam_message(self, event):
        await self.send_json(event["payload"])

    @staticmethod
    async def _aget_attempt_if_owner(attempt_id: int, student_id: int):
        try:
            return await ExamAttempt.objects.aget(id=attempt_id, student_id=student_id)
        except ExamAttempt.DoesNotExist:
            return None
