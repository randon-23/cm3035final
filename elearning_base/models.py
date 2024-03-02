from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone

def user_img_directory_path(instance, filename):
    return 'profile_imgs/user_{0}/{1}'.format(instance.user_id, filename)

def course_img_directory_path(instance, filename):
    return 'course_imgs/course_{0}/{1}'.format(instance.course_id, filename)

def activity_material_file_directory_path(instance, filename):
    return 'course_files/course_{0}/activity_{1}/files/{2}'.format(instance.course_activity.course.course_id, instance.course_activity.activity_id, filename)

def activity_material_image_directory_path(instance, filename):
    return '{0}/activity_{1}/images/{2}'.format(instance.course_activity.course.course_id, instance.course_activity.activity_id, filename)

def submission_directory_path(instance, filename):
    return 'submissions/user_{0}/activity_{1}/{2}'.format(instance.student.user_id, instance.course_activity.activity_id, filename)

#Overriding the default user model to add additional fields
class UserProfile(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    bio = models.TextField(max_length=500, blank=True)
    is_teacher = models.BooleanField(default=False, null=False, blank=False)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_img = models.ImageField(upload_to=user_img_directory_path, blank=True)

    def __str__(self):
        return f"Username: {self.username}\nIs Teacher? {self.is_teacher}"

    def clean(self):
        if '@' not in self.email:
            raise ValidationError("Invalid email format")
        
    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        
        Group.objects.get_or_create(name='Students')
        Group.objects.get_or_create(name='Teachers')

        if self.is_teacher:
            teachers = Group.objects.get(name='Teachers')
            self.groups.add(teachers)
        else:
            students = Group.objects.get(name='Students')
            self.groups.add(students)

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_title = models.CharField(max_length=100, unique=True, blank=False, null=False)
    course_img = models.ImageField(upload_to=course_img_directory_path, blank=True)
    description = models.TextField(max_length=1000, blank=False, null=False)
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_title}"
    
    def clean(self):
        if self.teacher.is_teacher == False:
            raise ValidationError("Only teachers can create courses")

# Bridge table for the many-to-many relationship between UserProfile and Course
class Enrollments(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    COMPLETE = 'Complete'
    BLOCKED = 'Blocked'

    ENROLLMENT_STATUSES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (COMPLETE, 'Complete'),
        (BLOCKED, 'Blocked')
    ]
    enrollment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, blank=False, null=False, choices=ENROLLMENT_STATUSES, default='Active')
    blocked = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return f"{self.student}\n\n{self.course}"
    
    def clean(self):
        if self.student.is_teacher == True:
            raise ValidationError("Only students can enroll in courses")
        
        valid_statuses = {choice[0] for choice in self.ENROLLMENT_STATUSES}
        if self.status not in valid_statuses:
            raise ValueError({'status': "Invalid status."})
    
    def save(self, *args, **kwargs):
        if self.blocked and self.status != self.BLOCKED:
            self.status = self.BLOCKED
        elif not self.blocked and self.status == self.BLOCKED:
            self.status = self.ACTIVE
        super(Enrollments, self).save(*args, **kwargs)
    
    class Meta:
        unique_together = ('course', 'student')

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
    file = models.FileField(upload_to=activity_material_file_directory_path, blank=True)
    video_link = models.URLField(blank=True)
    image = models.ImageField(upload_to=activity_material_image_directory_path, blank=True)

    def __str__(self):
        return f"{self.course_activity}\nMaterial Title: {self.material_title}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    course_activity = models.ForeignKey(CourseActivity, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=submission_directory_path, blank=False, null=False)
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
            
class StatusUpdate(models.Model):
    status_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='status_updates')
    status = models.TextField(max_length=1000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.status_id}"
    
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='feedback')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    feedback = models.TextField(max_length=1000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feedback_id}"
    
    def clean(self):
        if self.student.is_teacher == True:
            raise ValidationError("Only students can provide feedback")

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(max_length=1000, blank=False, null=False)
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    read = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_id}"
    
class LobbyMessage(models.Model):
    message_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='lobby_messages')
    message = models.TextField(max_length=1000, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_id}"
    
    
#Why overwrite model save function to automatically clean when saving?
#Ensures model is always validated before saving to the database
#Important as not always guaranteed that the model will be validated before saving
#However, a seperate clean call can be chosen where full validation is necessary before saving
#Such as form handling and specific views or services that manage model instances
#Validation logic might also vary and be dependent on the context in which model is being saved
#Also performance overhead in cleaning automatically with every save
            
