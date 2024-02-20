from rest_framework import serializers
from .models import *
from datetime import datetime

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'profile_img']

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

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserProfileSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['course_id', 'course_title', 'course_img', 'description', 'teacher', 'created_at', 'updated_at']

class EnrollmentsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = UserProfileSerializer(read_only=True)

    class Meta:
        model = Enrollments
        fields = ['enrollment_id', 'course', 'student', 'enrolled_at', 'status', 'blocked']