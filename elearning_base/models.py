from django.db import models
from django.contrib.auth.models import AbstractUser

#Overriding the default user model to add additional fields
class UserProfile(AbstractUser):
    user_id = models.AutoField(primary_key=True),
    email = models.EmailField(unique=True, blank=False, null=False),
    bio = models.TextField(max_length=500, blank=True),
    is_teacher = models.BooleanField(default=False, null=False, blank=False),
    date_of_birth = models.DateField(blank=True, null=True),
    profile_img = models.ImageField(upload_to='profile_imgs', blank=True)

    def __str__(self):
        return f"User ID: {self.user_id}\nUsername: {self.username}\nIs Teacher? {self.is_teacher}"

class Course(models.Model):
    course_id = models.AutoField(primary_key=True),
    title = models.CharField(max_length=100, blank=False, null=False),
    course_img = models.ImageField(upload_to='course_imgs', blank=True),
    description = models.TextField(max_length=1000, blank=False, null=False),
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='courses'),
    created_at = models.DateTimeField(auto_now_add=True),
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Course ID:{self.course_id}\nCourse Title: {self.title}"
    
class Tag(models.Model):
    tag_name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    
    def __str__(self):
        return f"{self.tag_name}"

class CourseTag(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_tags'),
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='course_tags')

    def __str__(self):
        return f"Course: {self.course}\nTag: {self.tag}"

# Bridge table for the many-to-many relationship between UserProfile and Course
class Enrollments(models.Model):
    enrollment_id = models.AutoField(primary_key=True),
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments'),
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='enrollments'),
    enrolled_at = models.DateTimeField(auto_now_add=True),
    blocked = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"Student:\n{self.student}\nCourse:\n{self.course}"

class CourseActivity(models.Model):
    LECTURE = 'LECTURE'
    ASSIGNMENT = 'ASSIGNMENT'
    EXAM = 'EXAM'

    COURSE_ACTIVITY_TYPES = [
        (LECTURE, 'Lecture'),
        (ASSIGNMENT, 'Assignment'),
        (EXAM, 'Exam')
    ]

    activity_id = models.AutoField(primary_key=True),
    activity_title = models.CharField(max_length=100, blank=False, null=False),
    description = models.TextField(max_length=1000, blank=False, null=False),
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_activities'),
    course_activity_type = models.CharField(max_length=15, blank=False, null=False, choices=COURSE_ACTIVITY_TYPES, default='LECTURE'),
    created_at = models.DateTimeField(auto_now_add=True),
    updated_at = models.DateTimeField(auto_now=True),
    deadline = models.DateTimeField(blank=True, null=True) #enforce in application logic

    def __str__(self):
        return f"Activity ID:{self.activity_id}\nCourse:{self.course}\nActivity:{self.activity_title}"
    
    class Meta:
        unique_together = ('title', 'course')

class CourseActivityMaterial(models.Model):
    material_id = models.AutoField(primary_key=True),
    material_title = models.CharField(max_length=100, blank=False, null=False),
    description = models.TextField(max_length=1000, blank=False, null=False),
    course_activity = models.ForeignKey(CourseActivity, on_delete=models.CASCADE, related_name='activity_materials'),
    created_at = models.DateTimeField(auto_now_add=True),
    updated_at = models.DateTimeField(auto_now=True),
    file = models.FileField(upload_to='activity_materials', blank=True),
    video_link = models.URLField(blank=True),
    image = models.ImageField(upload_to='activity_materials', blank=True)

    def __str__(self):
        return f"Material ID:{self.material_id}\nCourse Activity: {self.course_activity}\nTitle: {self.material_title}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True),
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions'),
    course_activity = models.ForeignKey(CourseActivity, on_delete=models.CASCADE, related_name='submissions'),
    submitted_at = models.DateTimeField(auto_now_add=True),
    file = models.FileField(upload_to='submissions', blank=False, null=False),
    grade = models.DecimalField(max_digits=5, decimal_places=0, blank=True, null=True)

    def __str__(self):
        return f"{self.submission_id} - {self.student} - {self.course_activity}"
    
