from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ProctorIQ.utils import IsTeacher, IsStudent
from django.shortcuts import get_object_or_404
from .serializers import TeacherSerializer, StudentSerializer, ChangePasswordSerializer, CustomTokenObtainPairSerializer, UpdateTeacherSerializer, UpdateStudentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
# from rest_framework.exceptions import ValidationError

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomUserView(APIView):
    permission_classes = [IsTeacher | IsStudent]

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
        # teachers only can create their profile
        data = request.data.copy()
        data['role'] = 'Teacher'
        serializer = TeacherSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

            # check old password
            if not user.check_password(old_password):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # validate new password
            try:
                validate_password(new_password, user)
            except DjangoValidationError as e:
                return Response(
                    {"password": e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # if valid, set the new password
            user.set_password(new_password)
            user.save()
            return Response(
                {"detail": "Password updated successfully."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    # need to complate this view
    pass

class StudentView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, pk=None):
        if pk:
            student = get_object_or_404(CustomUser, pk=pk, role='Student')

            if student.role != 'Student':
                return Response({"detail": "Student Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
            if student.created_by != request.user:
                return Response({"detail": "Not authorized to view this student."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = StudentSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)

        students = CustomUser.objects.filter(role='Student', created_by=request.user)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentViewForTeacher(APIView):
    permission_classes = [IsTeacher]

    def post(self, request: Request):

        if not request.user.subscribe:
            return Response({"detail": "You need to have a subscription to create students."}, status=status.HTTP_403_FORBIDDEN)
        
        nums_of_students = CustomUser.objects.filter(role='Student', created_by=request.user).count()
        print(nums_of_students)
        print(request.user.subscribe.nums_of_students)
        if nums_of_students >= request.user.subscribe.nums_of_students:
            return Response({"detail": "You have reached the maximum number of students allowed by your subscription. You need to upgrade."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['role'] = 'Student'
        data['created_by'] = request.user.id

        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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
    
    
