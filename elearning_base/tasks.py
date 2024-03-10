from celery import shared_task
from django.contrib.auth import get_user_model
from celery.utils.log import get_task_logger
from .models import Enrollments, Notification, CourseActivity, Course
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()
log = get_task_logger(__name__)

@shared_task(autoretry_for=(Exception,), retry_backoff=True)
def send_enrollment_notification(enrollment_id):
    try:
        enrollment = Enrollments.objects.get(enrollment_id=enrollment_id)
        teacher = enrollment.course.teacher
        notification = Notification.objects.create(
            title="New Enrollment",
            recipient=enrollment.course.teacher, 
            message=f"New enrollment for course {enrollment.course.course_title} - {enrollment.student.username}"
        )
        # Send notification via channels to teacher
        channel_layer = get_channel_layer()
        group_name = f"enrollment_notifications_{teacher.user_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,  # Group name where all notification listeners are added
            {
                "type": "new.notification",  # Custom event type name
                "message": notification.message,
                "title": notification.title,
            }
        )

        # Notify corresponding enrollment student client to subscribe to course-specific notifications
        # Dynamically adds user to course-specific notification groups when they enroll in a new course
        # Without this, the user will not receive any notifications for the new course until they refresh the page (resubscribe to the notification consumer)
        student_personal_group = f"user_notifications_{enrollment.student.user_id}"
        course_material_group = f"new_material_notifications_{enrollment.course.course_id}"
        course_activity_group = f"new_activity_notifications_{enrollment.course.course_id}"
        async_to_sync(channel_layer.group_send)(
            student_personal_group,
            {
                "type": "dynamic.subscription",
                "material_group": course_material_group,
                "activity_group": course_activity_group,
                "title": enrollment.course.course_title,
                "message": f"Welcome to {enrollment.course.course_title}! You will now receive notifications for new materials and activities in this course."
            }
        )
    except Enrollments.DoesNotExist:
        log.error("Enrollment does not exist")

@shared_task(autoretry_for=(Exception,), retry_backoff=True)
def send_new_material_notification(student_id, course_activity, course, material_title):
    try:
        student = User.objects.get(user_id=student_id)
        course_activity = CourseActivity.objects.get(activity_id=course_activity)
        course = Course.objects.get(course_id=course)
        notification = Notification.objects.create(
            title="New Material",
            recipient=student,
            message=f"New material {material_title} added to course '{course.course_title}'  -> activity: '{course_activity.activity_title}'"
        )
        # Send notification via channels to all enrolled students

        channel_layer = get_channel_layer()
        group_name = f"new_material_notifications_{course.course_id}_{student.user_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "new.notification",
                "message": notification.message,
                "title": notification.title
            }
        )
    except (User.DoesNotExist, CourseActivity.DoesNotExist, Course.DoesNotExist):
        log.error("Error in sending new material notification")

@shared_task(autoretry_for=(Exception,), retry_backoff=True)
def send_new_activity_notification(student_id, course, activity_title):
    try:
        student = User.objects.get(user_id=student_id)
        course = Course.objects.get(course_id=course)
        notification = Notification.objects.create(
            title="New Activity",
            recipient=student,
            message=f"New activity {activity_title} added course '{course.course_title}'"
        )

        # Send notification via channels to all enrolled students
        channel_layer = get_channel_layer()
        group_name = f"new_activity_notifications_{course.course_id}_{student.user_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "new.notification",
                "message": notification.message,
                "title": notification.title
            }
        )
    except (User.DoesNotExist, Course.DoesNotExist):
        log.error("Error in sending new activity notification")