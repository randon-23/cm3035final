from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import datetime 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_status_update(request):
    if request.method == 'POST':
        serializer = StatusUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    if request.method == 'POST':
        serializer = CourseCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course_activity(request, course_id):
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_course_acivity_material(request, course_id, activity_id):
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data, context={'request': request, 'course': course })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_enrollment(request):
    if request.method == 'POST':
        # No need to manually add student=request.user here, as it's done in serializer's create method
        serializer = EnrollmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # student is added in the serializer's create method
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_blocked_status(request, enrollment_id):
    if request.method == 'PATCH' or request.method == 'POST':
        try:
            enrollment = Enrollments.objects.get(pk=enrollment_id)

            if request.user != enrollment.course.teacher:
                return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)

            enrollment.blocked = not enrollment.blocked
            enrollment.save()

            serializer = EnrollmentUpdateSerializer(enrollment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Enrollments.DoesNotExist:
            return Response({'message': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_status_updates(request, user_id):
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        status_updates = StatusUpdate.objects.filter(user=user).order_by('-created_at')
        serializer = StatusUpdateSerializer(status_updates, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enrolled_courses(request, user_id):
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        courses = Enrollments.objects.filter(student=user).order_by('-enrolled_at')
        serializer = EnrollmentsSerializer(courses, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses_taught(request, user_id):
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        courses_taught = Course.objects.filter(teacher=user).order_by('-created_at')
        serializer = CourseSerializer(courses_taught, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_results(request, search_query):
    if request.method == 'GET':
        courses = Course.objects.filter(course_title__icontains=search_query)
        teachers = UserProfile.objects.filter(username__icontains=search_query, is_teacher=True)
        students = UserProfile.objects.filter(username__icontains=search_query, is_teacher=False)

        course_serializer = CourseSerializer(courses, many=True, context={'request': request})
        teachers_serializer = UserProfileSerializer(teachers, many=True, context={'request': request})
        students_serializer = UserProfileSerializer(students, many=True, context={'request': request})
        if request.user.is_teacher:
            results_dict = {'courses': course_serializer.data, 'teachers': teachers_serializer.data, 'students': students_serializer.data}
        else:
            results_dict = {'courses': course_serializer.data, 'teachers': teachers_serializer.data}
        return JsonResponse(results_dict, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_activities_with_materials(request, course_id):
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_feedback(request, course_id):
    try:
        course = Course.objects.get(course_id=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        feedbacks = Feedback.objects.filter(course=course).order_by('-created_at')
        serializer = FeedbackSerializer(feedbacks, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_enrolled_students(request, course_id):
    if request.method=='GET':
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        students = Enrollments.objects.filter(course=course).order_by('-enrolled_at')
        serializer = EnrollmentsSerializer(students, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class GetAvailableCourses(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'elearning_base/get_available_courses.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        return Course.objects.all().order_by('course_title')
        
    

        