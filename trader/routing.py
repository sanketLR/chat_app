from django.urls import path
from . import consumers

websocket_urlpatterns = [

    path('ws/Trade/', consumers.TradeConsumer.as_asgi()),
    
]