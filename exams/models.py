from django.db import models

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='created_exams')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def is_active(self):
        from django.utils import timezone
        return self.date >= timezone.now().date()    
    

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('tf', 'True/False')
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    def __str__(self):
        return f"{self.text[:50]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class ExamAttempt(models.Model):
    student = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title}"
    

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.question.question_type == 'mcq' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)
        if self.question.question_type == 'tf' and self.selected_choice:
            self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)

