from django.urls import path

from . import views

urlpatterns = [
    path("", views.checkin_view, name="checkin"),
]