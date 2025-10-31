from django.urls import path
from .views import (CustomUserView, ResetPasswordView,
                    CustomTokenObtainPairView, ChangePasswordView,
                    StudentViewForTeacher, StudentView)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/', CustomUserView.as_view(), name='custom_user_view'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('students/', StudentView.as_view(), name='student_view'),
    path('students/<int:student_id>/', StudentView.as_view(), name='student_detail_view'),
    path('create-student/', StudentViewForTeacher.as_view(), name='create_student'),
    path('update-student/<int:student_id>/', StudentViewForTeacher.as_view(), name='update_student'),
]
