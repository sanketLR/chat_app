from django.urls import path
from . import consumers

websocket_urlpatterns = [

    path('ws/grouptchat/<str:name>/', consumers.SimpleChatConsumer.as_asgi()),

]
