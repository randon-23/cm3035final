from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .models import *
from .forms import *
from .api import *
#redirect when successful action that modifies data to prevent duplicate submissions if the user refreshes
#render when displaying data or template with context directly to user without changing URL in browser

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #next_url = request.GET.get('next', 'home')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'elearning_base/login.html', {'form': form})
    
def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
        else:
            return render(request, 'elearning_base/register.html', {'form': form, 'error': f'Error in validating registration - {form.errors}'})
    else:
        form = UserForm()
        return render(request, 'elearning_base/register.html', {'form': form})

#Overriding the default logout view to redirect to login page after logout
class LogoutView(LogoutView):
    next_page = 'login'

@login_required
def home_view(request):
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
    profile_user=get_object_or_404(UserProfile, pk=user_id)
    is_own_profile = request.user.user_id == user_id

    status_update_response = get_status_updates(request, user_id)
    status_updates = json.loads(status_update_response.content) if status_update_response.status_code == 200 else {}
    
    if profile_user.is_teacher:
        courses_taught_response = get_courses_taught(request, user_id)
        courses_taught = json.loads(courses_taught_response.content) if courses_taught_response.status_code == 200 else {}
        
        context = {
            'is_own_profile': is_own_profile,
            'profile_user': profile_user,
            'status_updates': status_updates,
            'courses_taught': courses_taught
        }
    else:    
        enrollments_response = get_enrolled_courses(request, user_id)
        enrolled_courses = json.loads(enrollments_response.content) if enrollments_response.status_code == 200 else {}

        context = {
            'is_own_profile': is_own_profile,
            'profile_user': profile_user,
            'status_updates': status_updates,
            'enrolled_courses': enrolled_courses
        }

    return render(request, 'elearning_base/home.html', context)

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
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
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.teacher = request.user
            new_course.save()

            return redirect('get_enrolled_taught_courses')
    else:
        form = CourseForm()
    return render(request, 'elearning_base/create_course.html', {'form': form})

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
    pass

def password_reset_view(request):
    pass