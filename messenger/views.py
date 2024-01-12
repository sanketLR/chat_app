from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from . models import *
from . serializers import *
import time
from  . utils import *
from django.contrib.auth import (
    login, 
    logout
)

def simpleChat(request):
    return render(request, "simplechat.html")

def signUp(request):
    return render(request, "signup.html")

class CreateOrGetUser(APIView):    

    permission_classes = [AllowAny]

    def post(self, request):
        with transaction.atomic():
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                if not user.is_active:
                    return get_response(status.HTTP_400_BAD_REQUEST, get_status_msg('USER_NOT_ACTIVE'), get_status_msg('ERROR_400'))
                    
                refresh, access = get_tokens_for_user(user) 
                login(request, user)
                res = serializer.data

                res["refresh"] = refresh
                res["access"] = access
                return get_response(status.HTTP_200_OK, res, get_status_msg('RETRIEVE'))

            return get_response(status.HTTP_400_BAD_REQUEST, get_serializer_error_msg(serializer.errors), get_status_msg('ERROR_400'))


class LoadChatData(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        room_name = "python_group"

        chat_room = Chat_Room.objects.filter(cr_name=room_name).first().rooms.all()

        serializer = MessageSerializer(chat_room, many = True)
        
        if serializer is not None:
            time.sleep(1)
            return Response(
                {
                    "message" : "data retrived",
                    "result" : serializer.data,
                    "status" : status.HTTP_200_OK
                }
            )
        
        return Response(
            {
                "message" : "No data avaliable",
                "result" : [],
                "status" : status.HTTP_204_NO_CONTENT
            }
        )


class FlushRedisData(APIView):

    def post(self, request):

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.flush)()

        return Response({'status': 'success', 'message': 'Redis data flushed successfully'}, status=status.HTTP_200_OK)
    

class RetrieveAllRedisData(APIView):

    def get(self, request, *args, **kwargs):

        channel_layer = get_channel_layer()
        
        # Get all keys
        keys = async_to_sync(channel_layer.group_layer.keys)()
        
        # Retrieve corresponding values
        data = async_to_sync(channel_layer.group_layer.mget)(keys)
        
        return Response({'data': dict(zip(keys, data))})
