from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views
from . import api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Traditional views
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('users/<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('swagger_logout/', views.swagger_logout_view, name='swagger_logout'),
    path('update_profile/', views.update_profile_view, name='update_profile'),
    path('search/', views.search_view, name='search'),
    path('create_course/', views.create_course_view, name='create_course'),
    path('course/<int:course_id>/', views.course_view, name='course_page'),
    path('enrolled_taught_courses/', views.enrolled_taught_courses_view, name='enrolled_taught_courses'),
    path('enrolled_students/<int:course_id>/', views.enrolled_students_view, name='enrolled_students'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('lobby/', views.lobby_view, name='lobby'),
    
    #API Endpoints/REST Interface for all data required by user

    #Create
    path('api/create_user/', api.create_user_api, name='create_user_api'),
    path('api/create_status_update/', api.create_status_update, name='create_status_update'),
    path('api/create_course/', api.create_course, name='create_course_api'),
    path('api/create_feedback/<int:course_id>/', api.create_feedback, name='create_feedback'),
    path('api/create_enrollment/<int:course_id>', api.create_enrollment, name='create_enrollment'),
    path('api/create_course_activity/<int:course_id>/', api.create_course_activity, name='create_course_activity'),
    path('api/create_course_activity_material/<int:activity_id>/', api.create_course_activity_material, name='create_course_activity_material'),

    #Update
    path('api/update_blocked_status/<int:enrollment_id>/', api.update_blocked_status, name='update_blocked_status'),
    path('api/update_notification_read/<int:notification_id>/', api.update_notification_read, name='update_notification_read'),
    path('api/update_user/<int:user_id>/', api.update_user_api, name='update_user_api'),

    #Get
    path('api/get_status_updates/<int:user_id>/', api.get_status_updates, name='get_status_updates'),
    path('api/get_enrolled_courses/<int:user_id>/', api.get_enrolled_courses, name='get_enrolled_courses'),
    path('api/get_courses_taught/<int:user_id>/', api.get_courses_taught, name='get_courses_taught'),
    path('api/get_search_results/<str:search_query>/', api.get_search_results, name='get_search_results'),
    path('api/get_available_courses/', api.GetAvailableCourses.as_view(), name='get_available_courses'),
    path('api/get_enrolled_students/<int:course_id>/', api.get_enrolled_students, name='get_enrolled_students'),    
    path('api/get_course_feedback/<int:course_id>/', api.get_course_feedback, name='get_course_feedback'),
    path('api/get_course_activities/<int:course_id>/', api.get_course_activities_with_materials, name='get_course_activities_with_materials'),
    path('api/get_notifications/<int:user_id>/', api.get_notifications, name='get_notifications'),
    path('api/get_latest_lobby_messages/', api.get_latest_lobby_messages, name='get_latest_lobby_messages'),
    path('api/get_user/<int:user_id>/', api.get_user_api, name='get_user_api'),

    #Delete
    path('api/delete_status_update/<int:status_id>/', api.delete_status_update, name='delete_status_update'),
    path('api/delete_course_activity/<int:activity_id>/', api.delete_course_activity, name='delete_course_activity'),
    path('api/delete_user/<int:user_id>/', api.delete_user_api, name='delete_user_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)