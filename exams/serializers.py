from rest_framework import serializers
from .models import Exam, Question, Choice, ExamAttempt, StudentAnswer
from accounts.serializers import *

class ExamSerializer(serializers.ModelSerializer):
    created_by = TeacherSerializer(read_only=True) 
    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'duration_minutes', 'start_time', 'end_time', 'created_by', 'is_active']


class QuestionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)  
    class Meta:
        model = Question
        fields = ['id', 'exam', 'text', 'question_type', 'marks']


class ChoiceSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)  
    class Meta:
        model = Choice
        fields = ['id', 'question', 'text', 'is_correct']

class ExamAttemptSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)  
    exam = ExamSerializer(read_only=True)  
    class Meta:
        model = ExamAttempt
        fields = ['id', 'student', 'exam', 'started_at', 'ended_at', 'score']


class StudentAnswerSerializer(serializers.ModelSerializer):
    attempt = ExamAttemptSerializer(read_only=True)
    question = QuestionSerializer(read_only=True)  
    selected_choice = ChoiceSerializer(read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = ['id', 'attempt', 'question', 'selected_choice', 'text_answer', 'is_correct']


