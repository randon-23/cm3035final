from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]