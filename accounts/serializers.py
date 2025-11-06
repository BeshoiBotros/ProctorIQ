from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(user, 'role', 'CustomUser')

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = getattr(self.user, 'role', 'Unknown')
        return data


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'bio', 'image', 'phone_number', 'address', 'date_of_birth', 'role', 'subscribe']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email','password', 'image', 'phone_number', 'address', 'date_of_birth', 'role', 'created_by']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
class UpdateTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'image', 'phone_number', 'address', 'date_of_birth']

class UpdateStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'image', 'phone_number', 'address', 'date_of_birth']

class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True, required=True)

    new_password = serializers.CharField(write_only=True, required=True)

