import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing
import messenger.routing
import trader.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket":AuthMiddlewareStack(
        URLRouter(
            trader.routing.websocket_urlpatterns +
            messenger.routing.websocket_urlpatterns + 
            app.routing.websocket_urlpatterns
        )
    )
})
