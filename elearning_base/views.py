from django.shortcuts import render
from django.views.generic import *
import json
from .models import *
from .forms import *

def index(request):
    return render(request, 'elearning_base/index.html')
