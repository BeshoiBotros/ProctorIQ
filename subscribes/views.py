# subscriptions/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ProctorIQ.utils import IsTeacher
from .models import Subscribe
from .serializers import SubscribeSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

class AdminSubscribeView(APIView):
    
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            subscription = get_object_or_404(Subscribe, pk=pk)
            serializer = SubscribeSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)

        subscriptions = Subscribe.objects.all()
        serializer = SubscribeSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        data = request.data.copy()
        serializer = SubscribeSerializer(data=data)
        if serializer.is_valid():
            subscription = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        subscription = get_object_or_404(Subscribe, pk=pk)
        serializer = SubscribeSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subscription = get_object_or_404(Subscribe, pk=pk)
        subscription.delete()
        return Response({"detail": "Subscription deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class TeacherSubscribeView(APIView):


    permission_classes = [IsTeacher] 

    def post(self, request, pk):
        if request.user.subscribe:
            return Response({"detail": "You are already subscribed to a plan."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription = Subscribe.objects.get(pk=pk)
        except Subscribe.DoesNotExist:
            return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)

        request.user.subscribe = subscription
        request.user.save()

        return Response({"detail": f"You have successfully subscribed to the {subscription.title} plan."}, status=status.HTTP_200_OK)
    

    def patch(self, request, pk):
        
        if not request.user.subscribe:
            return Response({"detail": "You are not subscribed to a plan yet."}, status=status.HTTP_400_BAD_REQUEST)

        subscription = get_object_or_404(Subscribe, pk=pk)

        if request.user.subscribe.id == pk:
            return Response({"detail": "You are already subscribed to this plan."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.subscribe = subscription
        request.user.save()

        return Response({"detail": "Subscription updated successfully."}, status=status.HTTP_200_OK)

