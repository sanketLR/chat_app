from django.contrib import admin
from django.urls import path, include
from app.views import *
urlpatterns = [
  path("RetrieveAllRedisData/", RetrieveAllRedisData.as_view(), name="RetrieveAllRedisData")
]
