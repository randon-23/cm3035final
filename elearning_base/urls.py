from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views
from . import api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('users/<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('update_profile/', views.update_profile_view, name='update_profile'),

    #API Endpoints
    path('api/create_status_update/', api.create_status_update, name='create_status_update'),
    path('api/get_status_updates/<int:user_id>/', api.get_status_updates, name='get_status_updates')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)