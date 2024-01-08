from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('wc/sc/',consumers.MySyncConsumer.as_asgi()),
    path('wc/ac/',consumers.MyAsyncConsumer.as_asgi()),

    path('ws/Trade/', consumers.TradeConsumer.as_asgi()),
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]