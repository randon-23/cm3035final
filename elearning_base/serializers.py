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
    class Meta:
        model = Enrollments
        fields = []

    def validate(self, data):
        student = self.context['request'].user
        course = self.context['course']

        if course.teacher == student:
            raise serializers.ValidationError("Teacher cannot enroll in their own course.")
        
        if student.is_teacher:
            raise serializers.ValidationError("Teacher cannot enroll in courses.")
        
        if Enrollments.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("User is already enrolled in this course.")
        
        return data

    def create(self, validated_data):
        student = self.context['request'].user
        course = self.context['course']
        return Enrollments.objects.create(student=student, course=course)  
    
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
    
class CourseActivityMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseActivityMaterial
        fields = ['material_id', 'material_title', 'description', 'course_activity', 'created_at', 'updated_at', 'file', 'video_link', 'image']
        read_only_fields = ('material_id', 'course_activity', 'created_at', 'updated_at')
    
    def validate(self, data):
        # Object-level validation
        file = data.get('file')
        video_link = data.get('video_link')
        image = data.get('image')

        if not file and not video_link and not image:
            raise serializers.ValidationError("At least one of the following fields is required: file, video_link, image.")

        course_activity = self.context['course_activity']
        material_title = data['material_title']
        if CourseActivityMaterial.objects.filter(course_activity=course_activity, material_title=material_title).exists():
            raise serializers.ValidationError({"material_title": "Material with this title already exists for this activity."})

        return data

    def create(self, validated_data):
        course_activity = self.context['course_activity']
        return CourseActivityMaterial.objects.create(course_activity=course_activity, **validated_data)
    

class CourseActivitySerializer(serializers.ModelSerializer):
    activity_materials = CourseActivityMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = CourseActivity
        fields = ['activity_id', 'course', 'activity_title', 'description', 'activity_type', 'created_at', 'updated_at', 'deadline', 'activity_materials']
        read_only_fields = ('activity_id', 'course', 'created_at', 'updated_at', 'activity_materials')

    def validate_deadline(self, value):
        # Field-level validation for 'deadline'
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate(self, data):
        # Object-level validation
        activity_type = data.get('activity_type')
        deadline = data.get('deadline')

        if activity_type in [CourseActivity.ASSIGNMENT, CourseActivity.EXAM] and not deadline:
            raise serializers.ValidationError({"deadline": "Deadline is required for assignments and exams."})

        if deadline:
            # Assuming you want to enforce the deadline being at least one week from now for certain types
            one_week_ahead = timezone.now() + timezone.timedelta(weeks=1)
            if deadline < one_week_ahead:
                raise serializers.ValidationError({"deadline": "Deadline must be at least 1 week from now."})

        if activity_type == CourseActivity.LECTURE and deadline:
            raise serializers.ValidationError({"deadline": "Deadline is not required for lectures."})

        # Check for unique activity_title within the same course context
        course = self.context['course']
        activity_title = data['activity_title']
        if CourseActivity.objects.filter(course=course, activity_title=activity_title).exists():
            raise serializers.ValidationError({"activity_title": "Activity with this title already exists for this course."})

        return data

    def create(self, validated_data):
        # Assuming 'course' is added to the context in the view
        course = self.context['course']
        return CourseActivity.objects.create(course=course, **validated_data)
