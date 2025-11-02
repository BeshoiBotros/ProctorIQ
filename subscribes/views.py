# subscriptions/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ProctorIQ.utils import IsTeacher
from .models import Subscribe
from .serializers import SubscribeSerializer
from django.shortcuts import get_object_or_404
from .models import CustomUser

class SubscribeView(APIView):

    permission_classes = [IsTeacher]

# subscriptions/views.py

class SubscribeView(APIView):

    permission_classes = [IsTeacher]

    def get(self, request, pk=None):

        if not request.user.subscribe:
            return Response({"detail": "You are not subscribed to any plan."}, status=status.HTTP_400_BAD_REQUEST)
        
       
        if pk:
            if request.user.subscribe.id == pk:
                subscription = request.user.subscribe
                serializer = SubscribeSerializer(subscription)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "You are not authorized to access this subscription."}, status=status.HTTP_403_FORBIDDEN)

        subscription = request.user.subscribe
        serializer = SubscribeSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        
        if request.user.role != 'Teacher':
            return Response({"detail": "Only teachers can create subscriptions."}, status=status.HTTP_403_FORBIDDEN)

        if request.user.subscribe:
            return Response({"detail": "You already have a subscription."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['created_by'] = request.user.id

        serializer = SubscribeSerializer(data=data)
        if serializer.is_valid():
            subscription = serializer.save()
            
            
            request.user.subscribe = subscription  
            request.user.save()  
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):

        try:
            subscription = Subscribe.objects.get(pk=pk)
        except Subscribe.DoesNotExist:
            return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscribeSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        try:
            subscription = Subscribe.objects.get(pk=pk)
        except Subscribe.DoesNotExist:
            return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
    
        subscription.delete() 
        return Response({"detail": "Subscription deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
