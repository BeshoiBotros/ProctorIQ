from django.db import models
import uuid

class ProctoringSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_attempt = models.ForeignKey('exams.ExamAttempt', on_delete=models.CASCADE, related_name='proctoring_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Proctoring Session for {self.exam_attempt}"
    
class Frame(models.Model):
    session = models.ForeignKey(ProctoringSession, on_delete=models.CASCADE, related_name='frames')
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=f'proctoring_frames/{session}/')
    ai_result = models.JSONField(null=True, blank=True)
    suspicious_activity = models.BooleanField(default=False)

    def __str__(self):
        return f"Frame at {self.timestamp} for Session {self.session.id}"