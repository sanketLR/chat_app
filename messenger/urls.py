from django.contrib import admin
from django.urls import path, include
from messenger.views import *
urlpatterns = [
    
  path("signUp/", signUp, name="signUp"),
  path("signIn/", signIn, name="signIn"),
  path("simpleChat/<str:name>/", simpleChat, name="simpleChat"),
  path("rooms/", rooms, name="rooms"),

  path("CheckToken/", CheckToken.as_view(), name="CheckToken"),

  path("CreateUser/", CreateUser.as_view(), name="CreateUser"),
  path("SignInUser/", SignInUser.as_view(), name="SignInUser"),
  path("UserLogout/", UserLogout.as_view(), name="UserLogout"),

  path("RoomsCreate/", RoomsCreate.as_view(), name="RoomsCreate"),
  path("RoomsDelete/<int:id>/", RoomsDelete.as_view(), name="RoomsDelete"),
  path("RoomsList/", RoomsList.as_view(), name="RoomsList"),
  path("LoadChatData/", LoadChatData.as_view(), name="LoadChatData"),

  path("FlushRedisData/", FlushRedisData.as_view(), name="FlushRedisData"),
  path("RetrieveAllRedisData/", RetrieveAllRedisData.as_view(), name="RetrieveAllRedisData")
  
]
