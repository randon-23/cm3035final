from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'is_teacher', 'email')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'teacher')

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_name',)

class CourseTagAdmin(admin.ModelAdmin):
    list_display = ('course', 'tag')

class EnrollmentsAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'course', 'student')

class CourseActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_id', 'course', 'course_activity_type', 'title')

class CourseActivityMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'material_title', 'course_activity')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'course_activity', 'student', 'submitted_at', 'grade')

admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Tag)
admin.site.register(CourseTag)
admin.site.register(Enrollments)
admin.site.register(CourseActivity)
admin.site.register(CourseActivityMaterial)
admin.site.register(Submission)