from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Exam
from .serializers import ExamSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated  # Ensure user is authenticated
from ProctorIQ.utils import IsTeacher
from django.utils import timezone

# Create your views here.

class ExamView(APIView) : 
    permission_classes = [IsAuthenticated]

    def get(self, request, pk = None): 
        user = request.user


        if user.is_staff: 
            if pk:
                exam = get_object_or_404(Exam, pk=pk)
                serializer = ExamSerializer(exam)
                return Response(serializer.data, status=status.HTTP_200_OK)
            exams = Exam.objects.all()
            serializer = ExamSerializer(exams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        

        elif user.role == 'Teacher':
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

from .models import Exam, Question
from .serializers import QuestionSerializer
from ProctorIQ.utils import IsTeacher, IsStudent


class QuestionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, exam_id=None):

        user = request.user


        if user.is_staff:
            if pk:
                question = get_object_or_404(Question, pk=pk)
                serializer = QuestionSerializer(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


        elif user.role == 'Teacher':
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

    

            