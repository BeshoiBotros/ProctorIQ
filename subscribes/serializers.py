
from rest_framework import serializers
from .models import Subscribe

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['id', 'title', 'nums_of_exams', 'nums_of_students', 'price', 'description']
    

