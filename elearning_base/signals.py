from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollments, CourseActivity, CourseActivityMaterial, Course
from .tasks import send_enrollment_notification, send_new_material_notification, send_new_activity_notification
from channels.layers import get_channel_layer

@receiver(post_save, sender=Enrollments)
def enrollment_notification(sender, instance, created, **kwargs):
    if created:
        send_enrollment_notification.delay(instance.enrollment_id)

@receiver(post_save, sender=CourseActivityMaterial)
def course_activity_material_notification(sender, instance, created, **kwargs):
    if created:
        student_ids = Enrollments.objects.filter(course=instance.course_activity.course).values_list('student', flat=True)
        for student_id in student_ids:
            send_new_material_notification.delay(student_id, instance.course_activity.activity_id, instance.course_activity.course.course_id, instance.material_title)

@receiver(post_save, sender=CourseActivity)
def course_activity_notification(sender, instance, created, **kwargs):
    if created:
        student_ids = Enrollments.objects.filter(course=instance.course).values_list('student', flat=True)
        for student_id in student_ids:
            send_new_activity_notification.delay(student_id, instance.course.course_id, instance.activity_title)