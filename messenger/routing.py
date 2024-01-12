from django.urls import path
from . import consumers

websocket_urlpatterns = [

    path('ws/sc/', consumers.MySyncConsumer.as_asgi()),
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/grouptchat/python_chat/', consumers.SimpleChatConsumer.as_asgi()),

]
