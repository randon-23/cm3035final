from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
import random
import datetime 

@api_view(['GET', 'POST'])
def status_update(request=None):
    if request.method == 'POST':
