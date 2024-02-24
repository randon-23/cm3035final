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
    path('search/', views.search_view, name='search'),
    path('create_course/', views.create_course_view, name='create_course'),
    path('course/<int:course_id>/', views.course_view, name='course_page'),
    path('enrolled_taught_courses/', views.enrolled_taught_courses_view, name='enrolled_taught_courses'),
    path('enrolled_students/<int:course_id>/', views.enrolled_students_view, name='enrolled_students'),
    
    #API Endpoints - Done
    path('api/create_status_update/', api.create_status_update, name='create_status_update'),
    path('api/create_course/', api.create_course, name='create_course_api'),
    path('api/get_status_updates/<int:user_id>/', api.get_status_updates, name='get_status_updates'),
    path('api/get_enrolled_courses/<int:user_id>/', api.get_enrolled_courses, name='get_enrolled_courses'),
    path('api/get_courses_taught/<int:user_id>/', api.get_courses_taught, name='get_courses_taught'),
    path('api/get_search_results/<str:search_query>/', api.get_search_results, name='get_search_results'),
    path('api/get_available_courses/', api.GetAvailableCourses.as_view(), name='get_available_courses'),
    path('api/get_enrolled_students/<int:course_id>/', api.get_enrolled_students, name='get_enrolled_students'),
    path('api/update_blocked_status/<int:enrollment_id>/', api.update_blocked_status, name='update_blocked_status'),
    path('api/create_feedback/<int:course_id>/', api.create_feedback, name='create_feedback'),
    path('api/get_course_feedback/<int:course_id>/', api.get_course_feedback, name='get_course_feedback'),

    #API Endpoints - still need to be implemented
    path('api/create_course_activity/<int:course_id>', api.create_course_activity, name='create_course_activity'),
    path('api/add_course_activity_material/<int:course_id>/<int:activity_id>/', api.add_course_acivity_material, name='add_course_acivity_material'),
    path('api/create_enrollment/<int:course_id>', api.create_enrollment, name='create_enrollment'),
    path('api/get_course_activities/<int:course_id>/', api.get_course_activities_with_materials, name='get_course_activities_with_materials'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)