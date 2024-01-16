from django.contrib import admin
from django.urls import path, include
from messenger.views import *
urlpatterns = [
    
  path("signUp/", signUp, name="signUp"),
  path("signIn/", signIn, name="signIn"),
  path("simpleChat/", simpleChat, name="simpleChat"),
  path("rooms/", rooms, name="rooms"),

  path("CreateUser/", CreateUser.as_view(), name="CreateUser"),
  path("SignInUser/", SignInUser.as_view(), name="SignInUser"),
  path("UserLogout/", UserLogout.as_view(), name="UserLogout"),

  path("RoomsList/", RoomsList.as_view(), name="RoomsList"),
  path("LoadChatData/", LoadChatData.as_view(), name="LoadChatData"),

  path("FlushRedisData/", FlushRedisData.as_view(), name="FlushRedisData"),
  path("RetrieveAllRedisData/", RetrieveAllRedisData.as_view(), name="RetrieveAllRedisData")
  
]
