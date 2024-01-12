from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # path('wc/sc/',consumers.MySyncConsumer.as_asgi()),
    path('wc/ac/',consumers.MyAsyncConsumer.as_asgi()),
]