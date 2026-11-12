from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_detail, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("contacts/add/", views.contact_add, name="contact_add"),
    path("contacts/<int:pk>/edit/", views.contact_edit, name="contact_edit"),
    path("contacts/<int:pk>/remove/", views.contact_delete, name="contact_delete"),
]
