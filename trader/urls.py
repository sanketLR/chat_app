from django.contrib import admin
from django.urls import path, include
from trader.views import *
urlpatterns = [
  path("FlushRedisData/", FlushRedisData.as_view(), name="FlushRedisData"),
  path("RetrieveAllRedisData/", RetrieveAllRedisData.as_view(), name="RetrieveAllRedisData")
]
