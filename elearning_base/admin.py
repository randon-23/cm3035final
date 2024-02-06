from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username','email', 'is_teacher', 'date_of_birth', 'bio')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_title', 'description', 'teacher')

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_name',)

class CourseTagAdmin(admin.ModelAdmin):
    list_display = ('course', 'tag')

class EnrollmentsAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'course', 'student')

class CourseActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_id', 'course', 'activity_title', 'description', 'course_activity_type', 'deadline')

class CourseActivityMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'material_title', 'description', 'course_activity', 'file', 'video_link', 'image')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'student', 'course_activity', 'file', 'grade')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CourseTag, CourseTagAdmin)
admin.site.register(Enrollments, EnrollmentsAdmin)
admin.site.register(CourseActivity, CourseActivityAdmin)
admin.site.register(CourseActivityMaterial, CourseActivityMaterialAdmin)
admin.site.register(Submission, SubmissionAdmin)