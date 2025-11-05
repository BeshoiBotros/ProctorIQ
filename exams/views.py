from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Exam
from .serializers import ExamSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated 
from django.utils import timezone
from .models import *
from .serializers import *
from django.db.models import Avg, Max, Min, Count

# Create your views here.

class ExamView(APIView) : 
    permission_classes = [IsAuthenticated]

    def get(self, request, pk = None): 
        user = request.user
  
        if user.role == 'Teacher':
            if pk:
                exam = get_object_or_404(Exam, pk=pk, created_by = user)
                serializer = ExamSerializer(exam)
                return Response(serializer.data, status=status.HTTP_200_OK)

            exams = Exam.objects.filter(created_by = user)
            serializer = ExamSerializer(exams)
            return Response(serializer.data, status=status.HTTP_200_OK)

    
        elif user.role == 'Student':
            now = timezone.now()

            if pk:
                exam = get_object_or_404(
                    Exam.objects.filter(
                        is_active=True,
                        start_time__lte=now,
                        end_time__gte=now,
                        attempts__student=user  
                    ),
                    pk=pk
                )
                serializer = ExamSerializer(exam)
                return Response(serializer.data, status=status.HTTP_200_OK)

            exams = Exam.objects.filter(
                is_active=True,
                start_time__lte=now,
                end_time__gte=now,
                attempts__student=user  
            ).distinct()

            serializer = ExamSerializer(exams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)



    def post(self, request):
        user = request.user
        if user.role != 'Teacher':
            return Response({"detail": "Only teachers can create exams."}, status=status.HTTP_403_FORBIDDEN)


        data = request.data.copy()
        data['created_by'] = user.id  

        serializer = ExamSerializer(data = data)
        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = request.user

        exam = get_object_or_404(Exam, pk=pk)

        if user.role == 'Teacher' and exam.created_by != user:
            return Response({"detail": "You can only update exams you created."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ExamSerializer(exam, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        
        user = request.user

        exam = get_object_or_404(Exam, pk=pk)

        if user.role == 'Teacher' and exam.created_by != user:
            return Response({"detail": "You can only delete exams you created."}, status=status.HTTP_403_FORBIDDEN)

        exam.delete()
        return Response({"detail": "Exam deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class QuestionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, exam_id=None):

        user = request.user

        if user.role == 'Teacher':
            if exam_id:
                exam = get_object_or_404(Exam, id=exam_id, created_by=user)
                questions = exam.questions.all()
                serializer = QuestionSerializer(questions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            if pk:
                question = get_object_or_404(Question, pk=pk, exam__created_by=user)
                serializer = QuestionSerializer(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Exam ID is required to view questions."}, status=status.HTTP_400_BAD_REQUEST)


        elif user.role == 'Student':
            if not exam_id:
                return Response({"detail": "Exam ID is required."}, status=status.HTTP_400_BAD_REQUEST)


            exam = Exam.objects.filter(id=exam_id, attempts__student=user).first()
            if not exam:
                return Response({"detail": "You are not assigned to this exam."}, status=status.HTTP_403_FORBIDDEN)

            questions = exam.questions.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Unauthorized user role."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, exam_id=None):

        user = request.user

        if user.role != 'Teacher':
            return Response({"detail": "Only teachers can create questions."}, status=status.HTTP_403_FORBIDDEN)

        if not exam_id:
            return Response({"detail": "Exam ID is required to create a question."}, status=status.HTTP_400_BAD_REQUEST)


        exam = get_object_or_404(Exam, id=exam_id, created_by=user)

        data = request.data.copy()
        data['exam'] = exam.id

        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(exam=exam)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):

        user = request.user
        question = get_object_or_404(Question, pk=pk)

        if user.role == 'Teacher' and question.exam.created_by != user:
            return Response({"detail": "You can only update questions in your exams."}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuestionSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        user = request.user
        question = get_object_or_404(Question, pk=pk)

        if user.role == 'Teacher' and question.exam.created_by != user:
            return Response({"detail": "You can only delete questions in your exams."}, status=status.HTTP_403_FORBIDDEN)

        question.delete()
        return Response({"detail": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class ChoiceView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, question_id=None):
        user = request.user


        if user.role == 'Teacher':
            if question_id:
                question = get_object_or_404(Question, id=question_id, exam__created_by=user)
                choices = question.choices.all()
                serializer = ChoiceSerializer(choices, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if pk:
                choice = get_object_or_404(Choice, pk=pk, question__exam__created_by=user)
                serializer = ChoiceSerializer(choice)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({"detail": "Question ID is required to list choices."}, status=status.HTTP_400_BAD_REQUEST)


        elif user.role == 'Student':
            if not question_id:
                return Response({"detail": "Question ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.filter(
                id=question_id,
                exam__attempts__student=user
            ).first()

            if not question:
                return Response({"detail": "You are not allowed to view choices for this question."}, status=status.HTTP_403_FORBIDDEN)

            choices = question.choices.all()
            serializer = ChoiceSerializer(choices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Unauthorized role."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, question_id=None):
        user = request.user

        if user.role != 'Teacher':
            return Response({"detail": "Only teachers can create choices."}, status=status.HTTP_403_FORBIDDEN)

        if not question_id:
            return Response({"detail": "Question ID is required to create a choice."}, status=status.HTTP_400_BAD_REQUEST)

        question = get_object_or_404(Question, id=question_id, exam__created_by=user)

        data = request.data.copy()
        data['question'] = question.id

        serializer = ChoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):

        user = request.user
        choice = get_object_or_404(Choice, pk=pk)

        if user.role == 'Teacher' and choice.question.exam.created_by != user:
            return Response({"detail": "You can only update choices in your exams."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChoiceSerializer(choice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):


        user = request.user
        choice = get_object_or_404(Choice, pk=pk)

        if user.role == 'Teacher' and choice.question.exam.created_by != user:
            return Response({"detail": "You can only delete choices in your exams."}, status=status.HTTP_403_FORBIDDEN)

        choice.delete()
        return Response({"detail": "Choice deleted successfully."}, status=status.HTTP_204_NO_CONTENT)    
    
class ExamAttemptView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):

        user = request.user

        if user.role == 'Teacher':
            if pk:
                attempt = get_object_or_404(ExamAttempt, pk=pk, exam__created_by=user)
                serializer = ExamAttemptSerializer(attempt)
                return Response(serializer.data, status=status.HTTP_200_OK)

            attempts = ExamAttempt.objects.filter(exam__created_by=user)
            serializer = ExamAttemptSerializer(attempts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif user.role == 'Student':
            if pk:
                attempt = get_object_or_404(ExamAttempt, pk=pk, student=user)
                serializer = ExamAttemptSerializer(attempt)
                return Response(serializer.data, status=status.HTTP_200_OK)

            attempts = ExamAttempt.objects.filter(student=user)
            serializer = ExamAttemptSerializer(attempts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):

        user = request.user

        if user.role != 'Teacher':
            return Response({"detail": "Only teachers can assign exams."}, status=status.HTTP_403_FORBIDDEN)

        exam_id = request.data.get('exam')
        student_id = request.data.get('student')

        if not exam_id or not student_id:
            return Response({"detail": "Both 'exam' and 'student' fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        exam = get_object_or_404(Exam, id=exam_id, created_by=user)
        
        student = get_object_or_404(CustomUser, id=student_id, role='Student')

        if ExamAttempt.objects.filter(exam=exam, student=student).exists():
            return Response({"detail": "This student is already assigned to this exam."}, status=status.HTTP_400_BAD_REQUEST)

        attempt = ExamAttempt.objects.create(exam=exam, student=student)
        serializer = ExamAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):

        user = request.user
        attempt = get_object_or_404(ExamAttempt, pk=pk)


        if user.role == 'Student' and attempt.student != user:
            return Response({"detail": "You are not allowed to modify this attempt."}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action')

        if action == 'start':

            if attempt.started_at:
                return Response({"detail": "Exam already started."}, status=status.HTTP_400_BAD_REQUEST)
            attempt.started_at = timezone.now()
            attempt.save()
            return Response({"detail": "Exam started successfully."}, status=status.HTTP_200_OK)

        elif action == 'finish':
            if not attempt.started_at:
                return Response({"detail": "Exam has not started yet."}, status=status.HTTP_400_BAD_REQUEST)
            if attempt.ended_at:
                return Response({"detail": "Exam already finished."}, status=status.HTTP_400_BAD_REQUEST)

            attempt.ended_at = timezone.now()

            answers = attempt.answers.all()  
            total_questions = answers.count()

            if total_questions == 0:
                attempt.score = 0
                attempt.save()
                return Response({"detail": "Exam finished. No answers submitted.", "score": 0}, status=status.HTTP_200_OK)

            correct_answers = answers.filter(is_correct=True).count()

            total_marks = sum(a.question.marks for a in answers)
            earned_marks = sum(a.question.marks for a in answers if a.is_correct)

            attempt.score = round((earned_marks / total_marks) * 100, 2) if total_marks > 0 else 0

            attempt.save()

            return Response({
                "detail": "Exam finished successfully.",
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "total_marks": float(total_marks),
                "earned_marks": float(earned_marks),
                "score_percentage": float(attempt.score)
            }, status=status.HTTP_200_OK)
        
        return Response({"detail": "Invalid action. Use 'start' or 'finish'."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        user = request.user
        attempt = get_object_or_404(ExamAttempt, pk=pk)

        if user.is_staff or (user.role == 'Teacher' and attempt.exam.created_by == user):
            attempt.delete()
            return Response({"detail": "Exam attempt deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "You are not allowed to delete this attempt."}, status=status.HTTP_403_FORBIDDEN)

class StudentAnswerView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id=None):

        user = request.user

        if not attempt_id:
            return Response({"detail": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        attempt = get_object_or_404(ExamAttempt, id=attempt_id)
  
        if user.role == 'Teacher':
            if attempt.exam.created_by != user:
                return Response({"detail": "You can only view answers for your exams."}, status=status.HTTP_403_FORBIDDEN)
            answers = StudentAnswer.objects.filter(attempt=attempt)
            serializer = StudentAnswerSerializer(answers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


        if user.role == 'Student':
            if attempt.student != user:
                return Response({"detail": "You can only view your own answers."}, status=status.HTTP_403_FORBIDDEN)
            answers = StudentAnswer.objects.filter(attempt=attempt)
            serializer = StudentAnswerSerializer(answers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "Unauthorized role."}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, attempt_id=None):

        user = request.user

        if user.role != 'Student':
            return Response({"detail": "Only students can submit answers."}, status=status.HTTP_403_FORBIDDEN)

        if not attempt_id:
            return Response({"detail": "Attempt ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=user)

        question_id = request.data.get('question')
        choice_id = request.data.get('selected_choice')
        text_answer = request.data.get('text_answer', '')

        if not question_id:
            return Response({"detail": "Question ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        question = get_object_or_404(Question, id=question_id, exam=attempt.exam)

        now = timezone.now()
        if not (attempt.exam.start_time <= now <= attempt.exam.end_time):
            return Response({"detail": "The exam is not currently active."}, status=status.HTTP_400_BAD_REQUEST)

        selected_choice = None
        if question.question_type in ['mcq', 'tf'] and choice_id:
            selected_choice = get_object_or_404(Choice, id=choice_id, question=question)

        answer, created = StudentAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_choice': selected_choice,
                'text_answer': text_answer
            }
        )

        if selected_choice:
            answer.is_correct = selected_choice.is_correct
            answer.save()

        serializer = StudentAnswerSerializer(answer)
        message = "Answer submitted successfully." if created else "Answer updated successfully."
        return Response({"detail": message, "data": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk):

        user = request.user
        answer = get_object_or_404(StudentAnswer, pk=pk)

        if user.role == 'Teacher':
            if answer.attempt.exam.created_by != user:
                return Response({"detail": "You can only delete answers for your own exams."}, status=status.HTTP_403_FORBIDDEN)
            answer.delete()
            return Response({"detail": "Answer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)


class ExamResultsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        user = request.user

        exam = get_object_or_404(Exam, id=exam_id)

        if user.role != 'Teacher' or exam.created_by != user:
            return Response({"detail": "You are not authorized to view results for this exam."},
                            status=status.HTTP_403_FORBIDDEN)

        attempts = ExamAttempt.objects.filter(exam=exam).select_related('student')

        if not attempts.exists():
            return Response({"detail": "No students have attempted this exam yet."}, status=status.HTTP_200_OK)

        total_attempts = attempts.count()
        avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
        highest_score = attempts.aggregate(Max('score'))['score__max'] or 0
        lowest_score = attempts.aggregate(Min('score'))['score__min'] or 0

        student_results = [
            {
                "student_id": a.student.id,
                "student_name": a.student.username,
                "started_at": a.started_at,
                "ended_at": a.ended_at,
                "score": float(a.score) if a.score is not None else None
            }
            for a in attempts
        ]

        data = {
            "exam_id": exam.id,
            "exam_title": exam.title,
            "total_attempts": total_attempts,
            "average_score": round(float(avg_score), 2),
            "highest_score": round(float(highest_score), 2),
            "lowest_score": round(float(lowest_score), 2),
            "students": student_results
        }

        return Response(data, status=status.HTTP_200_OK)
