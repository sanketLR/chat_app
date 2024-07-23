from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from messenger.models import *
from messenger.serializers import *
import time
from chat_app.utils import *
from django.contrib.auth.models import User
from django.contrib.auth import (
    login, 
    logout
)
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import check_password, make_password
from urllib.parse import urlencode
from django.utils.crypto import get_random_string


def signUp(request):
    return render(request, "signup.html")


def signIn(request):

    if request.user.is_authenticated:
        return redirect("rooms")
    
    return render(request, "signin.html")


def rooms(request):
    return render(request, "rooms.html")


def simpleChat(request, name):
    
    name = Chat_Room.objects.filter(cr_name = name).first()
    
    if name == None:
        context = {
            "room_name" : ""
        }
        return render(request, "simplechat.html", context)
    context = {
        "room_name" : name.cr_name
    }
    return render(request, "simplechat.html", context)


# class GoogleLoginApi(APIView):
#     permission_classes = [AllowAny]

#     class InputSerializer(serializers.Serializer):
#         code = serializers.CharField(required=False)
#         error = serializers.CharField(required=False)

#     def post(self, request, *args, **kwargs):
#         input_serializer = self.InputSerializer(data=request.data)
#         input_serializer.is_valid(raise_exception=True)

#         validated_data = input_serializer.validated_data

#         code = validated_data.get('code')
#         error = validated_data.get('error')

#         login_url = f'{settings.BASE_FRONTEND_URL}/login'
    
#         if error or not code:
#             params = urlencode({'error': error})
#             return redirect(f'{login_url}?{params}')

#         redirect_uri = f'{settings.BASE_FRONTEND_URL}/google/'
#         access_token = google_get_access_token(code=code, 
#                                                redirect_uri=redirect_uri)
        
#         print('➡ chat_app/messenger/views.py:80 access_token:', access_token)

#         user_data = google_get_user_info(access_token=access_token)

#         try:
#             user = User.objects.get(email=user_data['email'])
#             access_token, refresh_token = generate_tokens_for_user(user)
#             response_data = {
#                 'user': UserSerializer(user).data,
#                 'access_token': str(access_token),
#                 'refresh_token': str(refresh_token)
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             username = user_data['email'].split('@')[0]
#             first_name = user_data.get('given_name', '')
#             last_name = user_data.get('family_name', '')

#             user = User.objects.create(
#                 username=username,
#                 email=user_data['email'],
#                 first_name=first_name,
#                 last_name=last_name,
#                 registration_method='google',
#                 phone_no=None,
#                 referral=None
#             )
         
#             access_token, refresh_token = generate_tokens_for_user(user)
#             response_data = {
#                 'user': UserSerializer(user).data,
#                 'access_token': str(access_token),
#                 'refresh_token': str(refresh_token)
#             }
#             return Response(response_data, status=status.HTTP_201_CREATED)

class GoogleLoginApi(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        error = request.query_params.get('error')
        base_frontend_url = os.getenv('DJANGO_BASE_FRONTEND_URL')
        login_url = f'{base_frontend_url}/api/messenger/signIn/'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = f'{base_frontend_url}/api/messenger/auth/login/google/'
        try:
            access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        user_data = google_get_user_info(access_token=access_token)
        print('➡ chat_app/messenger/views.py:142 user_data:', user_data)

        try:
            user = User.objects.get(email=user_data['email'])
            print('➡ chat_app/messenger/views.py:145 user:', user)
        except User.DoesNotExist:
            username = user_data['email'].split('@')[0]
            print('➡ chat_app/messenger/views.py:148 username:', username)
            first_name = user_data.get('given_name', '')
            print('➡ chat_app/messenger/views.py:150 first_name:', first_name)
            last_name = user_data.get('family_name', '')
            print('➡ chat_app/messenger/views.py:152 last_name:', last_name)

            # Set a random password
            password = get_random_string(length=32)
            user = User.objects.create(
                username=username,
                email=user_data['email'],
                first_name=first_name,
                last_name=last_name,
                password=make_password(password)
            )

        # Authenticate and login the user
        login(request, user)

        access_token, refresh_token = generate_tokens_for_user(user)
        response_data = {
            'user': UserSerializer(user).data,
            'access_token': str(access_token),
            'refresh_token': str(refresh_token)
        }
        Token = {
            "access" :access_token,
            "refresh" : refresh_token
        }
        # Redirect to rooms after login
        response = redirect(f'{base_frontend_url}/api/messenger/rooms/')
        response.set_cookie('access', access_token)
        response.set_cookie('refresh', refresh_token)
        return response


class CreateUser(APIView):    

    permission_classes = [AllowAny]

    def post(self, request):

        with transaction.atomic():

            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():

                password = request.data.get('password')
                user = serializer.save()
                user.password = make_password(password)
                user.save()

                if not user.is_active:
                    return get_response(status.HTTP_400_BAD_REQUEST, get_status_msg('USER_NOT_ACTIVE'), get_status_msg('ERROR_400'))
                    
                refresh, access = get_tokens_for_user(user) 
                
                res = serializer.data
                res["refresh"] = refresh
                res["access"] = access

                return get_response(status.HTTP_200_OK, res, get_status_msg('RETRIEVE'))
            return get_response(status.HTTP_400_BAD_REQUEST, get_serializer_error_msg(serializer.errors), get_status_msg('ERROR_400'))


class SignInUser(APIView):    

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not (username and password):
            return get_response(status.HTTP_400_BAD_REQUEST, get_status_msg('USER_PASS_REQ'), get_status_msg('ERROR_400'))
    
        user_obj = User.objects.filter(username=username).first()

        if user_obj == None:
            return get_response(status.HTTP_400_BAD_REQUEST, get_status_msg('USER_NOT_FOUND'), get_status_msg('ERROR_400'))

        chk_pass = check_password(password, user_obj.password)

        if chk_pass:
            user = authenticate(request=request, username=username, password=password)

            if user:
                refresh, access = get_tokens_for_user(user_obj) 
                login(request, user)
                Token = {
                    "access" :access,
                    "refresh" : refresh
                }
                return get_response(status.HTTP_200_OK, Token , get_status_msg('LOGGED_IN'))
        else:
            return get_response(status.HTTP_400_BAD_REQUEST, {} , get_status_msg('NOT_LOGGED_IN'))

     
class UserLogout(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = RefreshToken(request.data['refresh'])
            refresh_token.blacklist()
            logout(request) 
            return get_response(status.HTTP_200_OK, {} , get_status_msg('LOGGED_OUT'))
        except:
            return get_response(status.HTTP_400_BAD_REQUEST, {} , get_status_msg('INVALID_TOKEN'))


class CheckToken(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return get_response(status.HTTP_200_OK, {}, get_status_msg('CREATED'))


class RoomsCreate(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.is_superuser == False:
            return get_response(status.HTTP_400_BAD_REQUEST, {} , get_status_msg('NOT_ACCESS'))
        
        data = request.data

        serializer = ChatRoomSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            time.sleep(1)
            return get_response(status.HTTP_200_OK, serializer.data , get_status_msg('CREATED'))
        return get_response(status.HTTP_400_BAD_REQUEST, serializer.errors , get_status_msg('ERROR_400'))


class RoomsDelete(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, name):
        query_set = Chat_Room.objects.filter(cr_name = name).first()
        return query_set
    
    def post(self, request, name):
            
        room_queryset = self.get_queryset(name)

        serializer = ChatRoomSerializer(room_queryset)
        if serializer is not None:
            room_queryset.delete()
            return get_response(status.HTTP_200_OK, serializer.data , get_status_msg('DELETED'))
        return get_response(status.HTTP_404_NOT_FOUND, {} , get_status_msg('DATA_NOT_FOUND'))


class RoomsList(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        get_room_queryset =  Chat_Room.objects.all()

        serializer = ChatRoomSerializer(get_room_queryset, many = True)
        if serializer is not None:
            data = {
                "data": serializer.data,
                "superuser" : request.user.is_superuser
            }
            return get_response(status.HTTP_200_OK, data , get_status_msg('RETRIEVE'))
        return get_response(status.HTTP_400_BAD_REQUEST, {} , get_status_msg('NO_ROOMS'))


class LoadChatData(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        room_name = request.data
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
