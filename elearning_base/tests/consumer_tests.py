from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from elearning.asgi import application
from django.test import TransactionTestCase
from elearning_base.models import Course, Enrollments
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

User = get_user_model()

class TestNotificationConsumer(TransactionTestCase):
    async def asyncSetUp(self):
        self.student = await sync_to_async(User.objects.create_user)(username="test_student", password="test_password", email="test_student@test.com", is_teacher=False)
        self.teacher = await sync_to_async(User.objects.create_user)(username="test_teacher", password="test_password", email="test_teacher@test.com)", is_teacher=True)

        self.course = await sync_to_async(Course.objects.create)(course_title="Test Course", teacher=self.teacher)
        self.enrollment = await sync_to_async(Enrollments.objects.create)(student=self.student, course=self.course)
    
    async def test_notification_consumer_connected(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(application, f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_dynamic_subscription(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(application, f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Test student subscription to course-specific notifications
        channel_layer = get_channel_layer()
        user_group = f"user_notifications_{self.student.user_id}"
        material_group = f"new_material_notifications_{self.course.course_id}"
        activity_group = f"new_activity_notifications_{self.course.course_id}"

        await channel_layer.group_send(user_group, {
            "type": "dynamic.subscription", 
            "material_group": material_group, 
            "activity_group": activity_group
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["material_group"], material_group)
        self.assertEqual(response["activity_group"], activity_group)

        await communicator.disconnect()

    async def test_material_notification(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(application, f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        material_group = f"new_material_notifications_{self.course.course_id}"
        await channel_layer.group_send(material_group, {
            "type": "new.notification",
            "message": "New material added",
            "title": "New Material"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "New material added")
        self.assertEqual(response["title"], "New Material")

        await communicator.disconnect()
    
    async def test_notification_consumer(self):
        await self.asyncSetUp()
        communicator = WebsocketCommunicator(application, f"ws/notifications/")
        communicator.scope["user"] = self.student

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        channel_layer = get_channel_layer()
        activity_group = f"new_activity_notifications_{self.course.course_id}"
        await channel_layer.group_send(activity_group, {
            "type": "new.notification",
            "message": "New activity added",
            "title": "New Activity"
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response["message"], "New activity added")
        self.assertEqual(response["title"], "New Activity")

        await communicator.disconnect()