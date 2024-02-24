from rest_framework import serializers
from .models import *
from datetime import datetime

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['url', 'username', 'first_name', 'last_name', 'is_teacher', 'profile_img']
        extra_kwargs = {
            'url': {'view_name': 'user_profile', 'lookup_field': 'user_id'}
        }

class StatusUpdateSerializer(serializers.ModelSerializer):
    # Nested serializer to include user details in the response
    user = UserProfileSerializer(read_only=True) 
    #Customizing/overriding the errro field for a blank status
    status = serializers.CharField(error_messages={'blank': 'Status update cannot be empty.'})

    class Meta:
        model = StatusUpdate
        fields = ['status_id', 'user', 'status', 'created_at']
        read_only_fields = ('status_id', 'user', 'created_at')  # Read-only as they are not included in the POST request
        # but can be included in the response when getting posts.

    #Ensuring status is not empty
    def validate_status(self, value):
        if not value.strip():
            raise serializers.ValidationError("Status update cannot be empty.")
        return value
    
    def create(self, validated_data):
        user = validated_data.pop('user')
        return StatusUpdate.objects.create(user=user, **validated_data)

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    teacher = UserProfileSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['url', 'course_id', 'course_title', 'course_img', 'description', 'teacher', 'created_at', 'updated_at']
        extra_kwargs = {
            'url': {'view_name': 'course_page', 'lookup_field': 'course_id'}
        }
    

class CourseCreateSerializer(serializers.ModelSerializer):
    course_img = serializers.ImageField(required=False)
    class Meta:
        model = Course
        fields = ['course_title', 'description', 'course_img']

    def create(self, validated_data):
        # Extracting the course_img from the validated data so I can add it after the course has been created
        # So that I can use the course_id to name the image file path at time of saving image to model instance
        course_img = validated_data.pop('course_img', None)

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            teacher = UserProfile.objects.get(user_id=user.user_id)
        else:
            raise serializers.ValidationError("Teacher must be set but corresponding user not found.")
        
        validated_data.pop('teacher', None)
        course = Course.objects.create(teacher=teacher, **validated_data)

        # If there's an image, add it to the course instance
        if course_img:
            course.course_img = course_img
            course.save()

        return course

class EnrollmentsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = UserProfileSerializer(read_only=True)

    class Meta:
        model = Enrollments
        fields = ['enrollment_id', 'course', 'student', 'enrolled_at', 'status', 'blocked']

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollments
        fields = ['course']

    def validate(self, data):
        user = self.context['request'].user
        course = data['course']

        if course.teacher == user:
            raise serializers.ValidationError("Teacher cannot enroll in their own course.")
        
        if user.is_teacher:
            raise serializers.ValidationError("Teacher cannot enroll in courses.")
        
        if Enrollments.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError("User is already enrolled in this course.")
        
        return data

    def create(self, validated_data):
        course = validated_data.pop('course')
        user = self.context['request'].user

        enrollment = Enrollments.objects.create(course=validated_data['course'], student=user)

        return enrollment
    
class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollments
        fields = ['blocked']
    
class FeedbackSerializer(serializers.ModelSerializer):
    # Nested serializer to include user details in the response
    student = UserProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True) 
    #Customizing/overriding the errro field for a blank status
    feedback = serializers.CharField(error_messages={'blank': 'Status update cannot be empty.'})

    class Meta:
        model = Feedback
        fields = ['feedback_id', 'student', 'course', 'feedback', 'created_at']
        read_only_fields = ('feedback_id', 'student', 'course', 'created_at')  # Read-only as they are not included in the POST request
        # but can be included in the response when getting posts.

    #Ensuring status is not empty
    def validate_status(self, value):
        if not value.strip():
            raise serializers.ValidationError("Feedback cannot be empty.")
        return value
    
    def create(self, validated_data):
        student = self.context['request'].user
        course = self.context['course']
        return Feedback.objects.create(student=student, course=course, **validated_data)