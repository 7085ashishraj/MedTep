from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("facilities/", include("facilities.urls")),
    path("emergency/", include("emergency.urls")),
    path("first-aid/", include("firstaid.urls")),
    path("", include("core.urls")),
]
