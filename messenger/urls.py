from django.contrib import admin
from django.urls import path, include
from messenger.views import *
urlpatterns = [
    
  path("signUp/", signUp, name="signUp"),
  path("simpleChat/", simpleChat, name="simpleChat"),

  path("CreateOrGetUser/", CreateOrGetUser.as_view(), name="CreateOrGetUser"),
  path("LoadChatData/", LoadChatData.as_view(), name="LoadChatData"),

  path("FlushRedisData/", FlushRedisData.as_view(), name="FlushRedisData"),
  path("RetrieveAllRedisData/", RetrieveAllRedisData.as_view(), name="RetrieveAllRedisData")
  
]
