from django.urls import path

from . import views

app_name = "facilities"
urlpatterns = [
    path("", views.nearby, name="nearby"),
    path("api/nearby/", views.nearby_api, name="nearby_api"),
]
