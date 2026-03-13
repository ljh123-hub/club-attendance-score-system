from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_home, name='attendance_home'),
    path('meeting/create/', views.meeting_create, name='meeting_create'),
    path('meeting/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('checkin/<int:meeting_id>/', views.do_checkin, name='do_checkin'),
]