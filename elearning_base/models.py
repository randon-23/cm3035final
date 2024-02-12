from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone

#Overriding the default user model to add additional fields
class UserProfile(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.TextField(max_length=500, blank=True)
    is_teacher = models.BooleanField(default=False, null=False, blank=False)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_img = models.ImageField(upload_to='profile_imgs', blank=True)

    def __str__(self):
        return f"Username: {self.username}\nEmail: {self.email}\nIs Teacher? {self.is_teacher}"

    def clean(self):
        if '@' not in self.email:
            raise ValidationError("Invalid email format")

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_title = models.CharField(max_length=100, unique=True, blank=False, null=False)
    course_img = models.ImageField(upload_to='course_imgs', blank=True)
    description = models.TextField(max_length=1000, blank=False, null=False)
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Course Title: {self.course_title}"
    
    def clean(self):
        if self.teacher.is_teacher == False:
            raise ValidationError("Only teachers can create courses")
    
class Tag(models.Model):
    tag_name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    
    def __str__(self):
        return f"{self.tag_name}"

class CourseTag(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='course_tags')

    def __str__(self):
        return f"{self.course}\nTag: {self.tag}"
    
    class Meta:
        unique_together = ('course', 'tag')

# Bridge table for the many-to-many relationship between UserProfile and Course
class Enrollments(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"{self.student}\n\n{self.course}"
    
    def clean(self):
        if self.student.is_teacher == True:
            raise ValidationError("Only students can enroll in courses")

class CourseActivity(models.Model):
    LECTURE = 'LECTURE'
    ASSIGNMENT = 'ASSIGNMENT'
    EXAM = 'EXAM'

    COURSE_ACTIVITY_TYPES = [
        (LECTURE, 'Lecture'),
        (ASSIGNMENT, 'Assignment'),
        (EXAM, 'Exam')
    ]

    activity_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_activities')
    activity_title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=1000, blank=False, null=False)
    activity_type = models.CharField(max_length=15, blank=False, null=False, choices=COURSE_ACTIVITY_TYPES, default='LECTURE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(blank=True, null=True) #enforce in application logic

    def __str__(self):
        return f"{self.course}\nActivity Title: {self.activity_title}"
    
    class Meta:
        unique_together = ('activity_title', 'course')
    
    def clean(self):
        if self.deadline and self.deadline <= timezone.make_aware(datetime.now()):
            raise ValidationError("Deadline cannot be in the past")
        elif self.deadline and self.deadline < timezone.make_aware(datetime.now() + timedelta(weeks=1)):
            raise ValidationError("Deadline must be at least 1 week from now")
        
        valid_activity_types = {choice[0] for choice in self.COURSE_ACTIVITY_TYPES}
        if self.activity_type not in valid_activity_types:
            raise ValueError({'activity_type': "Invalid activity type."})


class CourseActivityMaterial(models.Model):
    material_id = models.AutoField(primary_key=True)
    material_title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(max_length=1000, blank=False, null=False)
    course_activity = models.ForeignKey(CourseActivity, on_delete=models.CASCADE, related_name='activity_materials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='activity_materials', blank=True)
    video_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='activity_materials', blank=True)

    def __str__(self):
        return f"{self.course_activity}\nMaterial Title: {self.material_title}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    course_activity = models.ForeignKey(CourseActivity, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions', blank=False, null=False)
    grade = models.DecimalField(max_digits=5, decimal_places=0, blank=True, null=True)

    def __str__(self):
        return f"{self.student}\n{self.course_activity}"
    
    def clean(self):
        if self.student.is_teacher == True:
            raise ValidationError("Only students can submit assignments")
        if self.course_activity.deadline and self.submitted_at > self.course_activity.deadline:
            raise ValidationError("Deadline has passed. Cannot submit documents anymore.")
        
        if self.grade is not None:
            if self.grade < 0:
                raise ValidationError("Grade cannot be negative")
            elif self.grade > 100:
                raise ValidationError("Grade cannot be greater than 100")

    
#Why overwrite model save function to automatically clean when saving?
#Ensures model is always validated before saving to the database
#Important as not always guaranteed that the model will be validated before saving
#However, a seperate clean call can be chosen where full validation is necessary before saving
#Such as form handling and specific views or services that manage model instances
#Validation logic might also vary and be dependent on the context in which model is being saved
#Also performance overhead in cleaning automatically with every save