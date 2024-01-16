from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path("api/user/",include("user.urls")),
    path("api/app/",include("app.urls")),
    path("api/messenger/",include("messenger.urls")),
    path("api/trader/",include("trader.urls")),
]
