from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Enrollments, Notification, CourseActivity, Course

User = get_user_model()

@shared_task
def send_enrollment_notification(enrollment_id):
    enrollment = Enrollments.objects.get(enrollment_id=enrollment_id)
    Notification.objects.create(
                            title="New Enrollment",
                            recipient=enrollment.course.teacher, 
                            message=f"New enrollment for course {enrollment.course.title} - {enrollment.student.user.username}"
    )

@shared_task
def send_new_material_notification(student_id, course_activity, course, material_title):
    student = User.objects.get(user_id=student_id)
    course_activity = CourseActivity.objects.get(activity_id=course_activity)
    course = Course.objects.get(course_id=course)
    Notification.obejcts.create(
        title="New Material",
        recipient=student,
        message=f"New material {material_title} added to following course -> activity: {course.course_title} -> {course_activity.activity_title}"
    )

@shared_task
def send_new_activity_notification(student_id, course, activity_title):
    student = User.objects.get(user_id=student_id)
    course = Course.objects.get(course_id=course)
    Notification.objects.create(
        title="New Activity",
        recipient=student,
        message=f"New activity {activity_title} added to following course -> {course.course_title}"
    )