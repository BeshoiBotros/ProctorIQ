from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError  
from django.contrib.auth.hashers import make_password


class CustomUser(AbstractUser):

    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    

class Teacher(CustomUser):
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=50, default='Teacher', editable=False)
    subscribe = models.ForeignKey('subscribes.Subscribe', on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

        permissions = [
            ("is_teacher", "Is a teacher"),
        ]

class Student(CustomUser):
    role = models.CharField(max_length=50, default='Student', editable=False)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        permissions = [
            ("can_view_student", "Can view student"),
            ("can_edit_student", "Can edit student"),
            ("can_delete_student", "Can delete student"),
            ("can_create_student", "Can create student"),
            ("can_edit_itself", "Student can edit self"),
            ('is_student', 'Is a student'),
        ]

