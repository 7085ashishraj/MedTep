from django.urls import path

from . import ambulance_views, views

app_name = "emergency"
urlpatterns = [
    path("sos/", views.start, name="start"),
    path("sos/create/", views.create, name="create"),
    path("sos/<uuid:pk>/", views.detail, name="detail"),
    path("ambulance/", ambulance_views.start, name="ambulance_start"),
    path("ambulance/request/<uuid:pk>/", ambulance_views.request_transport, name="ambulance_request"),
    path("ambulance/<int:pk>/", ambulance_views.detail, name="ambulance_detail"),
    path("ambulance/<int:pk>/status/", ambulance_views.status, name="ambulance_status"),
    path("operators/ambulances/", ambulance_views.dashboard, name="operator_dashboard"),
    path("operators/ambulances/<int:pk>/", ambulance_views.operator_update, name="operator_update"),
]
