from django.contrib import admin
from .models import CustomUser, Teacher, Student
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass

admin.site.register(Teacher)
admin.site.register(Student)