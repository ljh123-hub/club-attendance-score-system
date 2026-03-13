from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
<<<<<<< HEAD
    path('logout/', views.custom_logout, name='logout'),  # 使用自定义退出
=======
    path('logout/', views.custom_logout, name='logout'),
>>>>>>> 03f2d59 (feat: 优化界面风格，实现多部门选择及Tom Select交互)
]