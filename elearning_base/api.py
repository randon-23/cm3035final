from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from .models import *
from .serializers import *

# User specific views - These hasve been implemented partially
#Get user prpofile is used in the traditional view home. The rest are an implementation of the rest of the user data API.
#Can be implemented as additional features - weren't stipulated in assignment requirements.
#Create and update user profile are implemented as part of the user registration and update profile views via forms.
#Delete user profile is not a part of the application, however the endpoint can be successfully called by the user themselves to delete their own profile
@swagger_auto_schema(
    method='post',
    request_body=UserProfileCreateSerializer,
    responses={
        201: UserProfileCreateSerializer,
        400: 'Bad request',
        405: 'Method not allowed'
    },
    operation_description="Creates a user profile",
    tags=['User Profile']
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def create_user_api(request):
    if request.method == 'POST':
        serializer = UserProfileCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='patch',
    request_body=UserProfileCreateSerializer,
    responses={
        200: UserProfileCreateSerializer,
        400: 'Bad request',
        403: 'You are not authorized to perform this action',
        404: 'User not found',
        405: 'Method not allowed'
    },
    operation_description="Updates a user profile",
    tags=['User Profile']
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def update_user_api(request, user_id):
    try:
        user=UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        if request.user != user:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={
        200: UserProfileSerializer(many=True),
        403: 'As a student you are not authorized to view other student data!',
        404: 'User not found',
        405: 'Method not allowed'
    },
    operation_description="Get a user profile",
    tags=['User Profile']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_api(request, user_id):
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        if not user.is_teacher and not request.user.is_teacher and request.user != user:
            return Response({'message': 'As a student you are not authorized to view other student data!'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileSerializer(user, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@swagger_auto_schema(
    method='delete',
    responses={
        204: 'No Content',
        403: 'You are not authorized to perform this action',
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="Deletes a user profile",
    tags=['User Profile']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_api(request, user_id):
    if request.method == 'DELETE':
        try:
            user = UserProfile.objects.get(user_id=user_id)
            if request.user != user:
                return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# API endpoints for the rest of the models to create, update, dlete and get serialized data from the back-end

@swagger_auto_schema(
    method='post', 
    request_body=StatusUpdateSerializer, 
    responses={
        201: StatusUpdateSerializer,
        400: 'Bad request', 
        405: 'Method not allowed'
    },
    operation_description="Create a status update. The user is determined from the request.",
    tags=['User']
)
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

@swagger_auto_schema(
    method='post', 
    request_body=CourseCreateSerializer, 
    responses={
        201: CourseCreateSerializer, 
        400: 'Bad request', 
        403: 'You are not authorized to perform this action',
        405: 'Method not allowed'
    },
    operation_description="TEACHERS ONLY: Create a course. The teacher is determined from the request.",   
    tags=['Course']
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def create_course(request):
    if request.method == 'POST':
        if not request.user.has_perm('elearning_base.add_course'):
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='post', 
    request_body=CourseActivitySerializer, 
    responses={
        201: CourseActivitySerializer, 
        400: 'Bad request',
        403: 'You are not authorized to perform this action',
        404: 'Course not found', 
        405: 'Method not allowed'
    },
    operation_description="Create a course activity. The teacher is determined from the request.",
    tags=['Course']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course_activity(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if not request.user == course.teacher:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseActivitySerializer(data=request.data, context={'request': request, 'course': course})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='post', 
    request_body=CourseActivityMaterialSerializer,
    responses={
        201: CourseActivityMaterialSerializer,
        400: 'Bad request',
        404: 'Course or Activity not found',
        405: 'Method not allowed'
    },
    operation_description="Create a material for a course activity. The teacher is determined from the request body. File, image or URL must be appended to the request.",
    tags=['Course']
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def create_course_activity_material(request, activity_id):
    try:
        course_activity = CourseActivity.objects.get(pk=activity_id)
    except CourseActivity.DoesNotExist:
        return Response({'message': 'Course or Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if not request.user == course_activity.course.teacher:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CourseActivityMaterialSerializer(data=request.data, context={'request': request, 'course_activity': course_activity})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='post', 
    request_body=FeedbackSerializer, 
    responses={
        201: FeedbackSerializer,
        400: 'Bad request',
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="STUDENTS ONLY: Create a feedback for a course. The student is determined from the request.",
    tags=['Course']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        if not request.user.has_perm('elearning_base.add_feedback'):
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        #Check if enrolled in serializer
        serializer = FeedbackSerializer(data=request.data, context={'request': request, 'course': course })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='post', 
    request_body=EnrollmentCreateSerializer, 
    responses={
        201: EnrollmentCreateSerializer,
        400: 'Bad request',
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="STUDENTS ONLY - read till end: Enroll in a course. The student is determined by the request body. The serializer's create method sets the student to the request user. In doing so, the serializer has no expected fields as both student and course are determined via the context object.",
    tags=['Enrollment']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_enrollment(request, course_id):
    try:
        course=Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if not request.user.has_perm('elearning_base.add_enrollments'):
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        # No need to manually add student=request.user here, as it's done in serializer's create method
        serializer = EnrollmentCreateSerializer(data=request.data, context={'request': request, 'course': course})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    methods=['patch', 'post'], 
    request_body=EnrollmentUpdateSerializer,
    responses={
        200: EnrollmentUpdateSerializer,
        403: 'You are not authorized to perform this action',
        404: 'Enrollment not found',
        405: 'Method not allowed'
    },
    operation_description="Toggles the 'blocked' status of an enrollment. Determined server-side - not by the request body.",
    tags=['Course']
)
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

@swagger_auto_schema(
    methods=['patch', 'post'], 
    request_body=NotificationUpdateSerializer,
    responses={
        200: NotificationUpdateSerializer,
        403: 'You are not authorized to perform this action',
        404: 'Notification not found',
        405: 'Method not allowed'
    },
    operation_description="Toggles the 'read' status of a notification. Determined server-side - not by the request body.",
    tags=['Notifications']
)
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_notification_read(request, notification_id):
    if request.method == 'PATCH' or request.method == 'POST':
        try:
            notification = Notification.objects.get(pk=notification_id)

            if request.user != notification.recipient:
                return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)

            notification.read = not notification.read
            notification.save()

            serializer = NotificationUpdateSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'message': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get', 
    responses={
        200: StatusUpdateSerializer(many=True), 
        404: 'User not found', 
        405: 'Method not allowed'
    },
    operation_description="Get status updates for a given user",
    tags=['User']
)
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

@swagger_auto_schema(
    method='get', 
    responses={
        200: EnrollmentsSerializer(many=True),
        403: 'You are not authorized to perform this action', 
        404: 'User not found', 
        405: 'Method not allowed'
    },
    operation_description="Get enrolled courses for a given student user",
    tags=['Enrollments']
)
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

@swagger_auto_schema(
    method='get', 
    responses={
        200: CourseSerializer(many=True), 
        404: 'User not found', 
        405: 'Method not allowed'
    },
    operation_description="Get courses taught by a given teacher user",
    tags=['Course']
)
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

@swagger_auto_schema(
    method='get', 
    responses={
        200: openapi.Response(
            description="Search Results",
            schema=SearchResultSerializer
        ), 
        404: 'Search query not found', 
        405: 'Method not allowed'
    },
    operation_description="Get search results for a given search query. Results include courses, teachers and students; depending on request user type.",
    tags=['Miscellaneous']
)
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

@swagger_auto_schema(
    method='get',
    responses={
        200: CourseActivitySerializer(many=True),
        403: 'You are not authorized to perform this action',
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="If user is teacher or enrolled in course, Get course activities with materials for a given course",
    tags=['Course']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_activities_with_materials(request, course_id):
    try:
        course = Course.objects.get(course_id=course_id)
    except Course.DoesNotExist:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        enrolled = Enrollments.objects.filter(course=course, student=request.user, blocked=False).exists()
        if not enrolled and not request.user.is_teacher:
            return Response({'message': 'You are not authorized to perform this action. Enroll and try again!'}, status=status.HTTP_403_FORBIDDEN)
        
        activities = CourseActivity.objects.filter(course=course).order_by('-created_at')
        serializer = CourseActivitySerializer(activities, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={
        200: FeedbackSerializer(many=True),
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="Get feedback for a given course",
    tags=['Course']
)
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

@swagger_auto_schema(
    method='get',
    responses={
        200: EnrollmentsSerializer(many=True),
        403: 'You are not authorized to perform this action',
        404: 'Course not found',
        405: 'Method not allowed'
    },
    operation_description="Get enrolled students for a given course. Viewable only by the teacher of the course. Determined via request user.",
    tags=['Enrollments']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enrolled_students(request, course_id):
    if request.method=='GET':
        try:
            course = Course.objects.get(course_id=course_id)
        except Course.DoesNotExist:
            return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != course.teacher:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        students = Enrollments.objects.filter(course=course).order_by('-enrolled_at')
        serializer = EnrollmentsSerializer(students, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={
        200: NotificationSerializer(many=True),
        403: 'You are not authorized to perform this action',
        404: 'User not found',
        405: 'Method not allowed'
    },
    operation_description="Get notifications for a given user. Determined via request user. Can only view their own notifications",
    tags=['Notifications']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request, user_id):
    if request.method == 'GET':
        try:
            user = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != user:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        notifications = Notification.objects.filter(recipient=user, read=False).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={
        200: LobbyMessageSerializer(many=True),
        405: 'Method not allowed'
    },
    operation_description="Get the latest lobby messages. No permissions required, accessible by all users. Returns 10 latest messages in lobby.",
    tags=['Lobby']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_lobby_messages(request):
    if request.method == 'GET':
        latest_messages = LobbyMessage.objects.all().order_by('-created_at')[:10]
        serializer = LobbyMessageSerializer(latest_messages, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='delete',
    responses={
        204: 'No Content',
        403: 'You are not authorized to perform this action',
        404: 'Status update not found',
        405: 'Method not allowed'
    },
    operation_description="Delete a status update. The user is determined from the request. Users can only delete their own status updates.",
    tags=['User']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_status_update(request, status_id):
    if request.method == 'DELETE':
        try:
            status_update = StatusUpdate.objects.get(pk=status_id)
            if request.user != status_update.user:
                return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
            status_update.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except StatusUpdate.DoesNotExist:
            return Response({'message': 'Status update not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='delete',
    responses={
        204: 'No Content',
        403: 'You are not authorized to perform this action',
        404: 'Course Activity not found',
        405: 'Method not allowed'
    },
    operation_description="Delete a course activity. The teacher is determined from the request. Only the teacher of the course can delete course activities.",
    tags=['Course']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course_activity(request, activity_id):
    if request.method == 'DELETE':
        try:
            course_activity = CourseActivity.objects.get(pk=activity_id)
            if request.user != course_activity.course.teacher:
                return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
            course_activity.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CourseActivity.DoesNotExist:
            return Response({'message': 'Course Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#Gets list of available courses for students to enroll in
class GetAvailableCourses(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'elearning_base/get_available_courses.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        return Course.objects.all().order_by('course_title')
        
    

        