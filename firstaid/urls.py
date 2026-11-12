from django.urls import path

from . import views

app_name = "firstaid"
urlpatterns = [
    path("", views.guide_list, name="guide_list"),
    path("helplines/", views.helplines, name="helplines"),
    path("api/guides/", views.guide_list_api, name="guide_list_api"),
    path("api/guides/<slug:slug>/", views.guide_detail_api, name="guide_detail_api"),
    path("api/helplines/", views.helplines_api, name="helplines_api"),
    path("<slug:slug>/", views.guide_detail, name="guide_detail"),
]
