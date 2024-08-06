import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import messenger.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket":AuthMiddlewareStack(
        URLRouter(
            messenger.routing.websocket_urlpatterns 
        )
    )
})
