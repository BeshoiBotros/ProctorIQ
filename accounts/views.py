from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from ProctorIQ.utils import IsTeacher, IsStudent
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from .serializers import (
    TeacherSerializer, StudentSerializer, ChangePasswordSerializer,
    CustomTokenObtainPairSerializer, UpdateTeacherSerializer, UpdateStudentSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()] 
        return [IsAuthenticated()]  

    def get(self, request):
        user = request.user
        if user.role == 'Teacher':
            serializer = TeacherSerializer(user)
        elif user.role == 'Student':
            serializer = StudentSerializer(user)
        else:
            return Response({"detail": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'Teacher'
        data['is_active'] = True

        password = data.pop('password', None)
        if not password:
            return Response({"detail": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeacherSerializer(data=data)
        if serializer.is_valid():
            teacher = serializer.save()
            teacher.set_password(password) 
            teacher.save()
            return Response({
                "detail": "Teacher registered successfully.",
                "id": teacher.id,
                "username": teacher.username,
                "email": teacher.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request):
        user = request.user
        if user.role == 'Teacher':
            serializer = UpdateTeacherSerializer(user, data=request.data, partial=True)
        elif user.role == 'Student':
            serializer = UpdateStudentSerializer(user, data=request.data, partial=True)
        else:
            return Response({"detail": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsStudent | IsTeacher]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                validate_password(new_password, user)
            except DjangoValidationError as e:
                return Response({"password": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    pass


class StudentView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, pk=None):
        if pk:
            student = get_object_or_404(CustomUser, pk=pk, role='Student')

            if student.created_by != request.user:
                return Response({"detail": "Not authorized to view this student."}, status=status.HTTP_403_FORBIDDEN)

            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)

        students = CustomUser.objects.filter(role='Student', created_by=request.user)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentViewForTeacher(APIView):
    permission_classes = [IsTeacher]

from django.contrib.auth.hashers import make_password

class StudentViewForTeacher(APIView):
    permission_classes = [IsTeacher]

    def post(self, request: Request):
        if not request.user.subscribe:
            return Response({"detail": "You need to have a subscription to create students."},
                            status=status.HTTP_403_FORBIDDEN)

        nums_of_students = CustomUser.objects.filter(role='Student', created_by=request.user).count()
        if nums_of_students >= request.user.subscribe.nums_of_students:
            return Response({"detail": "You have reached the maximum number of students allowed by your subscription."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['role'] = 'Student'
        data['created_by'] = request.user.id
        data['is_active'] = True 

        password = data.get('password')
        if not password:
            return Response({"detail": "Password is required for student creation."},
                            status=status.HTTP_400_BAD_REQUEST)

        data['password'] = make_password(password)

        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            student = serializer.save()
            student.set_password(password) 
            student.save()
            return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request: Request, student_id: int):
        student = get_object_or_404(CustomUser, pk=student_id, role='Student')

        if student.created_by != request.user:
            return Response({"detail": "Not authorized to update this student."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdateStudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
