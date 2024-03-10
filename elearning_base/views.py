from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from .models import *
from .forms import *
from .api import *
#redirect when successful action that modifies data to prevent duplicate submissions if the user refreshes
#render when displaying data or template with context directly to user without changing URL in browser

# Traditional django views which handle the rendering of templates, processing of forms, 
#and calling of api functions to retrieve data from the backend to be unified in the template context object and displayed in the frontend.

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'elearning_base/login.html', {'form': form})
    
def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'elearning_base/register.html', {'form': form, 'error': f'Error in validating registration - {form.errors}'})
    else:
        form = UserForm()
        return render(request, 'elearning_base/register.html', {'form': form})

#Overriding the default logout view to redirect to login page after logout
class LogoutView(LogoutView):
    next_page = 'login'

#Swagger logout view - only used in development
def swagger_logout_view(request):
    logout(request)
    return redirect('schema-swagger-ui')

@login_required
def home_view(request):
    #In the users own profile, we are not retrieving the user profile via api call as we are in user_profile_view
    #But instead we are using the user object already available in the request
    status_update_form = StatusUpdateForm()
    status_update_response = get_status_updates(request, request.user.user_id)
    if status_update_response.status_code == 200:
        status_updates = json.loads(status_update_response.content)
    else:
        status_updates = {}
    
    if request.user.is_teacher:
        courses_taught_response = get_courses_taught(request, request.user.user_id)
        if courses_taught_response.status_code == 200:
            courses_taught = json.loads(courses_taught_response.content)
        else:
            courses_taught = {}
        
        context = {
        'is_own_profile': True,
        'profile_user': request.user,
        'form': status_update_form,
        'status_updates': status_updates,
        'courses_taught': courses_taught
    }
    else:
        enrollments_response = get_enrolled_courses(request, request.user.user_id)
        if enrollments_response.status_code == 200:
            enrolled_courses = json.loads(enrollments_response.content)
        else:
            enrolled_courses = {}

        context = {
        'is_own_profile': True,
        'profile_user': request.user,
        'form': status_update_form,
        'status_updates': status_updates,
        'enrolled_courses': enrolled_courses,
    }
    
    return render(request, 'elearning_base/home.html', context)

@login_required
def user_profile_view(request, user_id):
    #Added because if user accesses their own profile from search, the url used is not home but users/user_id
    #And so when a user accesses their own profile, they should be able to see the status update form
    status_update_form = StatusUpdateForm()

    is_own_profile = request.user.user_id == user_id

    profile_user_response=get_user_api(request, user_id)
    profile_user = json.loads(profile_user_response.content) if profile_user_response.status_code == 200 else {}
    print(profile_user)

    status_update_response = get_status_updates(request, user_id)
    status_updates = json.loads(status_update_response.content) if status_update_response.status_code == 200 else {}
    
    if profile_user.get('is_teacher'):
        courses_taught_response = get_courses_taught(request, user_id)
        courses_taught = json.loads(courses_taught_response.content) if courses_taught_response.status_code == 200 else {}
        
        context = {
            'is_own_profile': is_own_profile,
            'profile_user': profile_user,
            'status_updates': status_updates,
            'courses_taught': courses_taught,
            'form': status_update_form
        }
    else:    
        enrollments_response = get_enrolled_courses(request, user_id)
        enrolled_courses = json.loads(enrollments_response.content) if enrollments_response.status_code == 200 else {}

        context = {
            'is_own_profile': is_own_profile,
            'profile_user': profile_user,
            'status_updates': status_updates,
            'enrolled_courses': enrolled_courses,
            'form': status_update_form
        }

    return render(request, 'elearning_base/home.html', context)

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    return render(request, 'elearning_base/update_profile.html', {'form': form})

@login_required
def search_view(request):
    query = request.GET.get('query', '')
    search_results_response = get_search_results(request, query)
    search_results = json.loads(search_results_response.content) if search_results_response.status_code == 200 else {}

    context = {
        'courses': search_results.get('courses', []),
        'teachers': search_results.get('teachers', []),
        'students': search_results.get('students', []),
        'query': query
    }

    return render(request, 'elearning_base/search.html', context)

@login_required
def create_course_view(request):
    form = CourseForm()
    context = {
        'form': form
    }
    return render(request, 'elearning_base/create_course.html', context)

@login_required
def enrolled_taught_courses_view(request):
    if request.user.is_teacher:
        courses_taught_response = get_courses_taught(request, request.user.user_id)
        courses_taught = json.loads(courses_taught_response.content) if courses_taught_response.status_code == 200 else {}

        context = {
            'courses_taught': courses_taught
        }
    else:
        enrolled_courses_response = get_enrolled_courses(request, request.user.user_id)
        enrolled_courses = json.loads(enrolled_courses_response.content) if enrolled_courses_response.status_code == 200 else {}

        context = {
            'enrolled_courses': enrolled_courses
        }
    return render(request, 'elearning_base/enrolled_taught_courses.html', context)
    
@login_required
def course_view(request, course_id):
    feedback_form = FeedbackForm()
    course_activity_form = CourseActivityForm()
    course_activity_material_form = CourseActivityMaterialForm()

    course = get_object_or_404(Course, pk=course_id)
    feedback_response = get_course_feedback(request, course_id)
    course_feedback = json.loads(feedback_response.content) if feedback_response.status_code == 200 else {}
    course_activities_response = get_course_activities_with_materials(request, course_id)
    course_activities = json.loads(course_activities_response.content) if course_activities_response.status_code == 200 else {}

    is_creator = request.user.user_id == course.teacher.user_id
    is_enrolled = Enrollments.objects.filter(student=request.user, course=course).exists()
    is_teacher_viewer = request.user.is_teacher and not is_creator

    is_blocked = False
    if is_enrolled:
        enrollment = Enrollments.objects.get(student=request.user, course=course)
        is_blocked = enrollment.blocked

    context = {
        'course': course,
        'is_creator': is_creator,
        'is_enrolled': is_enrolled,
        'is_teacher_viewer': is_teacher_viewer,
        'is_blocked': is_blocked,
        'feedback_form': feedback_form,
        'course_activity_form': course_activity_form,
        'course_feedback': course_feedback,
        'course_activities': course_activities,
        'course_activity_material_form': course_activity_material_form
    }

    return render(request, 'elearning_base/course.html', context)

@login_required
def enrolled_students_view(request, course_id):
    enrollments_response = get_enrolled_students(request, course_id)
    enrollments = json.loads(enrollments_response.content) if enrollments_response.status_code == 200 else {}

    paginator = Paginator(enrollments, 10)  # Show 10 enrollments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'course_id': course_id    
    }
    return render(request, 'elearning_base/enrolled_students.html', context)

@login_required
def notifications_view(request):
    notifications_response = get_notifications(request, request.user.user_id)
    notifications = json.loads(notifications_response.content) if notifications_response.status_code == 200 else {}

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'notifications': notifications
    }
    return render(request, 'elearning_base/notifications.html', context)

@login_required
def lobby_view(request):
    latest_messages_response = get_latest_lobby_messages(request)
    latest_messages = json.loads(latest_messages_response.content) if latest_messages_response.status_code == 200 else []

    context = {
        'latest_messages': latest_messages
    }
    return render(request, 'elearning_base/lobby.html', context)