from django.shortcuts import render, redirect
from django.views.generic import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .models import *
from .forms import *
#redirect when successful action that modifies data to prevent duplicate submissions if the user refreshes
#render when displaying data or template with context directly to user without changing URL in browser

@login_required
def home(request):
    return render(request, 'elearning_base/home.html')

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

def password_reset_view(request):
    pass